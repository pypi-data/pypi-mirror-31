#!/usr/bin/env python
__author__ = "Gao Wang"
__copyright__ = "Copyright 2016, Stephens lab"
__email__ = "gaow@uchicago.edu"
__license__ = "MIT"
'''
This file defines methods to load and preprocess DSC scripts
'''

import os, re, itertools, copy, subprocess, platform, glob
from collections import Mapping, OrderedDict, Counter
from xxhash import xxh32 as xxh
from sos.utils import env
from sos.targets import fileMD5, executable
from .utils import FormatError, strip_dict, find_nested_key, get_nested_keys, merge_lists, flatten_list, uniq_list, \
     try_get_value, dict2str, set_nested_value, locate_file, filter_sublist, cartesian_list, yaml, \
     parens_aware_split, remove_parens, remove_quotes, rmd_to_r, update_gitignore
from .addict import Dict as dotdict
from .syntax import *
from .line import OperationParser, Str2List, EntryFormatter, parse_filter, parse_exe
from .plugin import Plugin
from .version import __version__
__all__ = ['DSC_Script', 'DSC_Pipeline', 'remote_config_parser']

class DSC_Script:
    '''Parse a DSC script
     * provides self.steps, self.runtime that contain all DSC information needed for a run
    '''
    def __init__(self, content, output = None, sequence = None, truncate = False, replicate = None):
        self.content = dict()
        if os.path.isfile(content):
            self._dsc_name = os.path.split(os.path.splitext(content)[0])[-1]
            script_path = os.path.dirname(os.path.expanduser(content))
            content = [x.rstrip() for x in open(content).readlines() if x.strip()]
        else:
            content = [x.rstrip() for x in content.split('\n') if x.strip()]
            if len(content) == 0:
                raise IOError(f"Invalid DSC script input!")
            if len(content) == 1:
                raise IOError(f"Cannot find file ``{content[0]}``")
            self._dsc_name = 'DSCStringIO'
            script_path = None
        res = []
        exe = ''
        headline = False
        for line in content:
            if line.lstrip().startswith('#'):
                continue
            text = parens_aware_split(line, ':')
            # FIXME: maybe this is good enough to identify a line of decorator keys ...
            if line.lstrip().startswith('@') and len(text) > 1:
                line = line.replace('@', '^', 1)
                text[0] = text[0].replace('@', '^', 1)
            if line.lstrip().startswith('*') and len(text) > 1:
                line = line.replace('*', '?', 1)
                text[0] = text[0].replace('*', '?', 1)
            if not DSC_BLOCK_CONTENT.search(line):
                headline = True
                if res:
                    self.update(res, exe)
                    res = []
                    exe = ''
                if len(text) != 2 or (len(text[1].strip()) == 0 and text[0].strip() != 'DSC' and not DSC_DERIVED_BLOCK.search(text[0].strip())):
                    raise FormatError(f'Invalid syntax ``{line}``. '\
                                      'Should be in the format of ``module names: module executables``')
                res.append(f'{text[0]}:')
                exe += text[1].strip().strip('\\')
            else:
                if headline and len(text) == 1:
                    # still contents for exe
                    exe += line.strip().strip('\\')
                else:
                    headline = False
                    if len(text) == 1:
                        # handle line break
                        res[-1] += ' ' + line.lstrip()
                    else:
                        res.append(line)
        self.update(res, exe)
        if 'DSC' not in self.content:
            if sequence is None:
                raise FormatError('Cannot find section ``DSC`` or command input ``--target`` that defines benchmarks to execute!')
            else:
                self.content['DSC'] = dict()
        global_vars = try_get_value(self.content, ('DSC', 'global'))
        self.set_global_vars(global_vars)
        self.content = EntryFormatter()(self.content, global_vars)
        derived, sorted_blocks = self.get_derived_blocks()
        for block in sorted_blocks:
            if block == 'DSC':
                continue
            self.extract_modules(block, derived[block] if block in derived else None)
        self.runtime = DSC_Section(self.content['DSC'], sequence, output, replicate)
        if self.runtime.output is None:
            self.runtime.output = self._dsc_name
        for k in self.runtime.sequence_ordering:
            if k not in self.content:
                raise FormatError(f"Module ``{k}`` is not defined!\nAvailable modules are ``{[x for x in self.content.keys() if x != 'DSC']}``")
        self.modules = dict([(x, DSC_Module(x, self.content[x], self.runtime.options, script_path, truncate))
                             for x in self.runtime.sequence_ordering.keys()])
        script_types =  [m.exe['type'] for m in self.modules.values()]
        if 'R' in script_types:
            self.runtime.rlib.append(f'dscrutils@stephenslab/dsc/dscrutils ({__version__}+)')
        if 'R' in script_types and 'PY' in script_types:
            self.runtime.pymodule.extend(['rpy2', 'dsc'])
        self.runtime.rlib.extend(flatten_list([x.rlib for x in self.modules.values() if x.rlib]))
        self.runtime.pymodule.extend(flatten_list([x.pymodule for x in self.modules.values() if x.rlib]))
        # FIXME: maybe this should be allowed in the future
        self.runtime.check_looped_computation()

    def update(self, text, exe):
        try:
            block = yaml.load('\n'.join(text))
        except Exception as e:
            if type(e).__name__ == 'DuplicateKeyError':
                raise FormatError(f"Duplicate keys found in\n``{self._dsc_name}.dsc``")
            else:
                env.logger.warning(e)
                raise FormatError(f"``{self._dsc_name}.dsc`` has caused ``{type(e).__name__}`` (see above).\nPlease ensure there is no duplicated variable names in modules. If this is related to string with quotes please remove them, or use the 'raw()' syntax.")
        for idx, k in enumerate(flatten_list(get_nested_keys(block))):
            self.validate_var_name(str(k), idx)
        name = re.sub(re.compile(r'\s+'), '', list(block.keys())[0])
        block[name] = block.pop(list(block.keys())[0])
        if block[name] is None:
            block[name] = dict()
        if not isinstance(block[name], Mapping):
            raise FormatError(f"Code block ``{name}`` has format issues! Please make sure variables follow from ``key:(space)item`` format.")
        if exe:
            exe = parse_exe(exe)
            block[name]['^EXEC'] = exe[0]
            for k, v in exe[1].items():
                if k in block[name] and block[name][k] != v:
                    raise FormatError(f"Block ``{name}`` has property conflicts for ``k``: ``{block[name][k]}`` or ``{v}``?")
                block[name][k] = v
        if name in self.content:
            raise FormatError(f'Duplicate block name ``{name}``.')
        self.content.update(block)

    def set_global_vars(self, gvars):
        if gvars is None:
            return
        for v in gvars:
            for block in self.content:
                keys = list(find_nested_key(v, self.content[block]))
                for k in keys:
                    set_nested_value(self.content[block], k, gvars[v])

    @staticmethod
    def validate_var_name(val, is_parameter):
        tip = f"If this limitation is irrelevant to your problem, and you really cannot rename variable in your code, then at your own risk you can rename ``{val}`` to, eg, ``name`` in DSC and use ``@ALIAS: {val} = name``."
        groups = DSC_DERIVED_BLOCK.search(val)
        if groups:
            val = (groups.group(1).strip(), groups.group(2).strip())
        else:
            val = (val,)
        val = flatten_list([[vv.strip() for vv in v.split(',') if vv.strip()] for v in val])
        for vv in val:
            if is_parameter == 0 and (not vv.isidentifier() or vv.startswith('_') or vv.endswith('_')):
                raise FormatError(f'Invalid module name ``{vv.replace("^", "?")}``')
            if is_parameter == 0:
                continue
            if vv.startswith('_') or vv.endswith('_'):
                raise FormatError(f"Names cannot start or end with underscore, in ``{vv}``. Note that such naming convention is not acceptable to R. {tip}")
            if '.' in vv:
                raise FormatError(f"Dot is not allowed for module / variable names, in ``{vv}``. Note that dotted names is not acceptable to Python and SQL. {tip}")
            if '$' in vv[1:] or vv == '$':
                raise FormatError(f"``$`` is not allowed in module / variable names, in ``{vv}``.")
            if '^' in vv[1:]:
                raise FormatError(f'Invalid variable name ``{vv}``')
            if not (vv == '?' or vv.startswith('^') or vv.startswith('$')):
                if not vv.isidentifier():
                    raise FormatError(f'Invalid variable name ``{vv.replace("^", "?")}``')

    def get_derived_blocks(self):
        '''
        input: name of derived blocks looks like: "derived(base)"
        output:
        - derived : {block_name: derived_block, base_block}
        - base: [module, ...]
        - sorted_keys: figures out sorted block names such that derived block always follows the base block
        '''
        base = []
        blocks = []
        derived = dict()
        for block in self.content:
            groups = DSC_DERIVED_BLOCK.search(block)
            if groups:
                derived[block] = (groups.group(1), groups.group(2))
                if ',' in derived[block][1]:
                    raise FormatError(f"Invalid base module name ``{derived[block][1]}``. Base module has to be single module.")
            else:
                base.extend(block.split(','))
                blocks.append(block)
        if len(derived) == 0:
            return derived, list(self.content.keys())
        # get module level derivation
        # [(derived, base), ()...]
        tmp = sum([cartesian_list(*[y.split(',') for y in x]) for x in derived.values()], [])
        # Check self-derivation and non-existing base
        for item in tmp:
            if item[0] == item[1]:
                raise FormatError(f"Looped block inheritance: {item[0]}({item[0]})!")
            if item[1] not in base and item[1] not in [x[0] for x in tmp]:
                raise FormatError(f"Base block ``{item[1]}`` does not exist for {item[0]}({item[1]})!")
        # now create duplicates by swapping
        # and looped derivations: x(y) and y(x)
        tmp = [sorted(x) for x in tmp]
        for item in ((i, tmp.count(i)) for i in tmp):
            if item[1] > 1:
                raise FormatError(f"Looped block inheritance: {item[0][0]}({item[0][1]}) and {item[0][1]}({item[0][0]})!")
        #
        derived_cycle = itertools.cycle(derived.values())
        while True:
            item = next(derived_cycle)
            if item[1] in base:
                base.extend(item[0].split(','))
                name = f'{item[0]}({item[1]})'
                if name not in blocks:
                    blocks.append(name)
            if len(blocks) == len(self.content.keys()):
                break
        return derived, blocks

    def extract_modules(self, block, derived):
        '''
        block: block raw name str
        derived: (derived modules str, base module str)
        '''
        res = dict()
        # expand module executables
        modules = block.split(',') if derived is None else derived[0].split(',')
        if len([x for n, x in enumerate(modules) if x in modules[:n]]):
            raise FormatError(f"Duplicate module in block ``{','.join(modules)}``.")
        if derived is not None and '^EXEC' not in self.content[block]:
            self.content[block]['^EXEC'] = [self.content[derived[1]]['meta']['exec']]
        if len(modules) != len(self.content[block]['^EXEC']) and len(self.content[block]['^EXEC']) > 1:
            raise FormatError(f"Block ``{', '.join(modules)}`` specifies ``{len(modules)}`` modules, yet ``{len(self.content[block]['^EXEC'])}`` executables are provided. Please ensure they match.")
        if len(modules) > 1 and len(self.content[block]['^EXEC']) == 1:
            self.content[block]['^EXEC'] = self.content[block]['^EXEC'] * len(modules)
        # collection module specific parameters
        tmp = dict([(module, dict([('global', dict()), ('local', dict())])) for module in modules])
        for key in self.content[block]:
            if key.startswith('^') and key not in DSC_MODP:
                # then possibly it is executables
                # we'll update executable specific information
                for m in key[1:].split(','):
                    if m.strip() not in modules:
                        raise FormatError(f'Undefined decoration ``@{m.strip()}/^{m.strip()}``.')
                    else:
                        for kk, ii in self.content[block][key].items():
                            if isinstance(ii, Mapping):
                                if not kk.startswith('^'):
                                    raise FormatError(f'Invalid decoration ``{kk}``. Decorations must start with ``@`` symbol.')
                                if kk not in DSC_MODP:
                                    raise FormatError(f'Undefined decoration ``@{kk[1:]}/^{kk[1:]}``.')
                                else:
                                    continue
                        tmp[m.strip()]['local'].update(self.content[block][key])
            elif key == '^EXEC':
                for idx, module in enumerate(modules):
                    tmp[module]['global'][key] = list(self.content[block][key][idx])
            elif key not in DSC_MODP and isinstance(self.content[block][key], Mapping):
                raise FormatError(f'Invalid decoration ``{key}``. Decorations must start with ``@`` symbol.')
            else:
                for module in modules:
                    tmp[module]['global'][key] = self.content[block][key]
        # parse input / output / meta
        # output has $ prefix, meta has . prefix, input has no prefix
        del self.content[block]
        for module in tmp:
            if module in self.content:
                raise FormatError(f'Duplicate module definition ``{module}``')
            if DSC_RESERVED_MODULE.search(module):
                raise FormatError(f'Invalid module name ``"{module}"``: cannot end with ``_[0-9]`` or conflict with DSC reserved keys.')
            if derived is not None:
                res[module] = copy.deepcopy(self.content[derived[1]])
            else:
                res[module] = dict([('input', dict()), ('output', dict()), ('meta', dict())])
            for item in ['global', 'local']:
                for key in tmp[module][item]:
                    if key.startswith('$'):
                        res[module]['output'][key[1:]] = uniq_list(tmp[module][item][key])
                    elif key.startswith('^'):
                        res[module]['meta'][key[1:].lower()] = tmp[module][item][key]
                    else:
                        res[module]['input'][key] = uniq_list(tmp[module][item][key])
        for module in res:
            conflict = [x for x in res[module]['input']
                        if x in res[module]['output'] and not (isinstance(res[module]['input'][x][0], str) and res[module]['input'][x][0].startswith('$'))]
            if len(conflict):
                raise FormatError(f"Name ``{conflict[0]}`` cannot be used for both parameter and output for module ``{module}``")
        self.content.update(res)

    @staticmethod
    def get_sos_options(name, content):
        out = dotdict()
        out.verbosity = env.verbosity
        out.__wait__ = True
        out.__no_wait__ = False
        out.__targets__ = []
        out.__queue__ = 'localhost'
        out.__remote__ = None
        out.dryrun = False
        out.__dag__ = f'.sos/.dsc/{name}.dot'
        # In DSC we will not support `resume` just to keep it simple
        out.__resume__ = False
        out.__config__ = f'.sos/.dsc/{name}.conf.yml'
        out.update(content)
        if '__max_running_jobs__' not in content:
            out.__max_running_jobs__ = 1
        if '__max_procs__' not in content:
            out.__max_procs__ = 1
        if '__bin_dirs__' not in content:
            out.__bin_dirs__ = []
        if 'workflow' not in content:
            out.workflow = 'default'
        return out

    def init_dsc(self, args, env):
        if args.__construct__ == 'none':
            import shutil
            shutil.rmtree('.sos')
        os.makedirs('.sos/.dsc', exist_ok = True)
        if os.path.dirname(self.runtime.output):
            os.makedirs(os.path.dirname(self.runtime.output), exist_ok = True)
        if env.verbosity > 2:
            env.logfile = os.path.basename(self.runtime.output) + '.log'
            if os.path.isfile(env.logfile):
                os.remove(env.logfile)
        if os.path.isfile('.sos/transcript.txt'):
            os.remove('.sos/transcript.txt')
        conf = '.sos/.dsc/{}.conf.yml'.format(os.path.basename(self.runtime.output))
        with open(conf, 'w') as f:
            f.write('localhost: localhost\nhosts:\n  localhost:\n    address: localhost')
        update_gitignore()

    def dump(self):
        res = dict([('Modules', self.modules),
                    ('DSC', dict([("Sequence", self.runtime.sequence),
                                  ("Ordering", [(x, y) for x, y in self.runtime.sequence_ordering.items()])]))])
        return res

    def __str__(self):
        res = '# Modules\n' + '\n'.join([f'## {x}\n```yaml\n{y}```' for x, y in self.modules.items()]) \
              + f'\n# DSC\n```yaml\n{self.runtime}```'
        return res

    def print_help(self):
        res = {'modules': OrderedDict([(' ', []), ('parameters', []),
                                       ('input', []), ('output', []), ('type', [])])}
        for k in self.content:
            if k == 'DSC':
                pipelines = self.content[k]['run']
                if isinstance(pipelines, Mapping):
                    pipelines = [(k, ', '.join(v)) for k, v in pipelines.items()]
                else:
                    pipelines = [(k+1, v) for k, v in enumerate(pipelines)]
                res['pipelines'] = '\n'.join([f'{x[0]}: ' + re.sub(r"\s\*\s", ' -> ', x[1]) for x in pipelines])
                if 'define' in self.content[k]:
                    res['groups'] = self.content[k]['define']
            else:
                res['modules'][' '].append(k)
                res['modules']['output'].append(', '.join(self.content[k]['output'].keys()))
                inputs = []
                params = []
                for x in self.content[k]['input']:
                    if isinstance(self.content[k]['input'][x][0], str) and self.content[k]['input'][x][0].startswith('$'):
                        inputs.append(x)
                    else:
                        params.append(x)
                res['modules']['input'].append(', '.join(inputs))
                res['modules']['parameters'].append(', '.join(params))
                res['modules']['type'].append(self.modules[k].exe['type'])
        from .prettytable import PrettyTable
        t = PrettyTable()
        for key, value in res['modules'].items():
            t.add_column(key, value)
        print('')
        env.logger.info("``MODULES``")
        print(t)
        print('')
        env.logger.info("``PIPELINES``")
        print(res['pipelines'] + '\n')
        env.logger.info("``PIPELINES EXPANDED``")
        print('\n'.join([f'{i+1}: ' + ' -> '.join(x) for i, x in enumerate(self.runtime.sequence)]) + '\n')
        if len([x for x in self.runtime.rlib if not x.startswith('dscrutils')]):
            from .utils import get_rlib_versions
            env.logger.info("``R LIBRARIES``")
            env.logger.info("Scanning package versions ...")
            libs, versions = get_rlib_versions(self.runtime.rlib)
            t = PrettyTable()
            t.add_column('name', libs)
            t.add_column('version', versions)
            print(t)
            print('')
        if len(self.runtime.pymodule):
            from .utils import get_pymodule_versions
            env.logger.info("``PYTHON MODULES``")
            libs, versions = get_pymodule_versions(self.runtime.pymodule)
            t = PrettyTable()
            t.add_column('name', libs)
            t.add_column('version', versions)
            print(t)
            print('')


class DSC_Module:
    def __init__(self, name, content, global_options = None, script_path = None, lite = False):
        # module name
        self.name = name
        # params: alias, value
        self.p = OrderedDict()
        # return variables: alias, value
        self.rv = OrderedDict()
        # return files: alias, ext
        self.rf = OrderedDict()
        # groups of parameters eg (n,p): (1,2)
        self.pg = []
        # exec
        self.exe = None
        # script plugin object
        self.plugin = None
        # runtime variables
        self.workdir = None
        self.libpath = None
        self.path = None
        self.libpath_tracked = None
        self.rlib = None
        self.pymodule = None
        # dependencies
        self.depends = []
        # check if it runs in shell
        # Now init these values
        self.set_options(global_options, try_get_value(content, ('meta', 'conf')))
        self.set_exec(content['meta']['exec'])
        self.set_input(try_get_value(content, 'input'), try_get_value(content, ('meta', 'alias')))
        self.set_output(content['output'])
        self.apply_input_operator()
        if lite:
            self.chop_input()
        # parameter filter:
        self.ft = self.apply_input_filter(try_get_value(content, ('meta', 'filter')))
        self.set_output_ext()

    @staticmethod
    def pop_lib(vec, lib):
        res = []
        for item in vec:
            if lib.search(item) and ';' not in item:
                res.append(vec.pop(vec.index(item)).strip())
        return '\n'.join(res), vec

    def set_exec(self, exe):
        '''
        Example input exec:
        - ['unknown', 'MSE.R']
        - ['R', 'mse = (mean_est-true_mean)^2']
        - ('unknown', 'datamaker.py split')
        '''
        # FIXME: need to handle $() in args ensure they exist in parameter list
        self.exe = {'path': [], 'content': [], 'args': None, 'signature': None,
                    'file': [], 'type': 'unknown', 'header': '', 'interpreter': None}
        for etype, item in zip(exe[0], exe[1:]):
            if etype != 'unknown':
                # is inline code
                if etype != self.exe['type']:
                    if self.exe['type'] == 'unknown':
                        self.exe['type'] = etype
                    else:
                        raise FormatError(f"Cannot mix ``{etype}`` and ``{self.exe['type']}`` codes, near ``{item}``.")
                self.exe['content'].append(item)
            else:
                # is executable
                item = item.split()
                etype = os.path.splitext(item[0])[1].lstrip('.').upper()
                is_rmd = False
                rmd_chunk_pattern = None
                self.exe['file'].append(item[0])
                if etype == 'RMD':
                    etype = 'R'
                    is_rmd = True
                    tmp_chunk_name = item[0].split('@')
                    if len(tmp_chunk_name) > 1:
                        rmd_chunk_pattern = tmp_chunk_name[0]
                        item[0] = tmp_chunk_name[-1]
                if len(item) > 1:
                    if self.exe['args'] is not None:
                        raise FormatError(f"Executable arguments conflict near ``{item[0]}``: ``{' '.join(self.exe['args'])}`` or ``{' '.join(item[1:])}``?")
                    else:
                        self.exe['args'] = item[1:]
                fpath = locate_file(item[0], self.path)
                if fpath is None:
                    # must be a system executable
                    self.exe['path'].append(item[0])
                    if etype in ['PY', 'R']:
                        env.logger.warning(f'Cannot find script ``{item[0]}`` in path ``{self.path}``. DSC will treat it a command line executable.')
                else:
                    # try determine self.exe['type']
                    if etype == '':
                        etype = 'unknown'
                    if self.exe['type'] == 'unknown':
                        self.exe['type'] = etype
                    if self.exe['type'] != etype:
                        raise FormatError(f"Cannot mix ``{etype}`` and ``{self.exe['type']}`` codes, near ``{item[0]}``.")
                    # load contents
                    if etype != 'unknown':
                        self.exe['content'].extend(open(fpath, 'r').readlines() if not is_rmd else rmd_to_r(fpath, chunk_pattern = rmd_chunk_pattern))
                    else:
                        self.exe['path'].append(fpath)
                if is_rmd:
                    env.logger.warning(f'Source code of ``{self.name}`` is loaded from ``{item[0]}``. This is only recommended for prototyping.')
        assert len(self.exe['path']) == 0 or len(self.exe['content']) == 0
        if len(self.exe['path']) > 1:
            raise FormatError(f"Cannot mix multiple executables ``{self.exe['path']}`` in one module ``{self.name}``.")
        if len(self.exe['path']):
            self.exe['path'] = self.exe['path'][0]
        if len(self.exe['path']) == 0 and len(self.exe['content']) == 0:
            raise FormatError(f"Contents in ``{self.exe['file']}`` is empty!")
        if self.exe['type'] == 'R':
            # check if Rscript command exists
            if self.exe['interpreter'] is None and not executable('Rscript').target_exists():
                raise ValueError(f'Executable ``Rscript`` is required to run module ``"{self.name}"`` yet is not available from command-line console.')
            # bump libraries import to front of script
            self.exe['header'], self.exe['content'] = self.pop_lib(self.exe['content'], DSC_RLIB)
            if self.rlib is not None:
                self.exe['header'] = '\n'.join([f'library({x.split()[0].split("@")[0]})' for x in self.rlib]) + \
                                     '\n' + self.exe['header']
        elif self.exe['type'] == 'PY':
            self.exe['header'], self.exe['content'] = self.pop_lib(self.exe['content'], DSC_PYMODULE)
            if self.pymodule is not None:
                self.exe['header'] = '\n'.join([f'import {x.split()[0]})' for x in self.pymodule]) + \
                                     '\n' + self.exe['header']
        self.exe['content'] = '\n'.join([x.rstrip() for x in self.exe['content']
                                         if x.strip() and not x.strip().startswith('#')])
        # scan for library signatures
        if self.libpath_tracked is not None:
            libs = [glob.glob(os.path.join(os.path.expanduser(x), f'*.{self.exe["type"]}')) for x in self.libpath_tracked]
            libs.extend([glob.glob(os.path.join(os.path.expanduser(x), f'*.{self.exe["type"].lower()}')) for x in self.libpath_tracked])
            lib_signature = ' '.join([fileMD5(x) for x in flatten_list(libs)])
        else:
            lib_signature = ''
        self.exe['signature'] = xxh((fileMD5(self.exe['path'], partial = False) if len(self.exe['path']) else self.exe['content']) + (' '.join(self.exe['args']) if self.exe['args'] else '') + lib_signature).hexdigest()
        self.plugin = Plugin(self.exe['type'], self.exe['signature'])

    def set_output_ext(self):
        # check if the exec is meant to be executed from shell
        # and set extension for automatic output
        # True only if self.exe['path']
        # Also this conflicts with self.rv: self.exe['path'] && len(self.rv) == 0
        if len(self.exe['path']) == 0 and len(self.rv) > 0:
            # make it a list in order to readily merge with other self.rf items
            self.rf['DSC_AUTO_OUTPUT_'] = ['rds' if self.plugin.name == 'R' else 'pkl']

    def set_output(self, return_var):
        '''
        Figure out if output is a variable, file or plugin
        '''
        if len(return_var) == 0:
            raise FormatError(f"Please specify output variables for module ``{self.name}``.")
        for key, value in return_var.items():
            if len(value) > 1:
                raise FormatError(f"Module output ``{key}`` cannot contain multiple elements ``{value}``")
            value = value[0]
            in_input = try_get_value(self.p, value)
            if in_input:
                # output is found in input
                # and input is potentially a list
                # so have to figure out if a file is involved
                for p in in_input:
                    if not isinstance(p, str):
                        continue
                    groups = DSC_FILE_OP.search(p)
                    if groups:
                        try:
                            self.rf[key].append(groups.group(1).strip('.'))
                        except Exception:
                            self.rf[key] = [groups.group(1).strip('.')]
                # are there remaining values not file()?
                if key in self.rf and len(self.rf[key]) < len(in_input):
                    raise FormatError(f"Return ``{key}`` in ``{in_input}`` cannot be a mixture of file() and module input")
            if key in self.rf:
                continue
            # now decide this new variable is a file or else
            if not isinstance(value, str):
                self.rv[key] = value
                continue
            groups = DSC_ASIS_OP.search(value)
            if groups:
                self.rv[key] = groups.group(1)
                continue
            # For file
            groups = DSC_FILE_OP.search(value)
            if groups:
                self.rf[key] = [groups.group(1).strip('.')]
            else:
                self.rv[key] = value

    def set_options(self, common_option, spec_option):
        if isinstance(spec_option, Mapping):
            valid = False
            for module in spec_option:
                if module == self.name or module == '?':
                    spec_option = spec_option[module]
                    valid = True
                    break
            if not valid:
                raise FormatError(f"Cannot find module ``{self.name}`` in @CONF specification ``{list(spec_option.keys())}``.")
        spec_option = dict([(x.strip() for x in item.split('=', 1)) for item in spec_option]) if spec_option is not None else dict()
        spec_option = {k: [remove_quotes(x) for x in Str2List()(remove_parens(v))] for k, v in spec_option.items()}
        # Override global options
        workdir1 = try_get_value(common_option, 'work_dir')
        workdir2 = try_get_value(spec_option, 'work_dir')
        libpath1 = try_get_value(common_option, 'lib_path')
        libpath2 = try_get_value(spec_option, 'lib_path')
        path1 = try_get_value(common_option, 'exec_path')
        path2 = try_get_value(spec_option, 'exec_path')
        self.workdir = workdir2 if workdir2 is not None else workdir1
        self.libpath = libpath2 if libpath2 is not None else libpath1
        self.path = path2 if path2 is not None else path1
        self.rlib = try_get_value(spec_option, 'R_libs')
        self.pymodule = try_get_value(spec_option, 'python_modules')
        self.libpath_tracked = libpath2

    def set_input(self, params, alias):
        if params is not None:
            # handle input groups (n,p):(1,2)
            for p in params:
                if ',' in p:
                    ps = parens_aware_split(remove_parens(p))
                    self.pg.append(ps)
                    for pp in ps:
                        if pp in self.p:
                            raise FormatError(f'Cannot add in duplicate parameter ``{pp}`` to module {self.name}')
                        else:
                            self.p[pp] = []
                    for item in params[p]:
                        if not isinstance(item, tuple) and len(item) == len(ps):
                            raise FormatError(f'Parameter group ``{p}`` and value ``{item}`` should have same length')
                        for pp, ii in zip(ps, item):
                            self.p[pp].append(ii)
                else:
                    if p not in self.p:
                        self.p[p] = params[p]
                    else:
                        raise FormatError(f'Cannot add in duplicate parameter ``{p}`` to module {self.name}')
        if isinstance(alias, Mapping):
            valid = False
            for module in alias:
                if module == self.name or module == '?':
                    alias = alias[module]
                    valid = True
                    break
            if not valid:
                raise FormatError(f"Cannot find module ``{self.name}`` in @ALIAS specification ``{list(alias.keys())}``.")
        if alias is not None:
            alias = [tuple(x.strip() for x in item.split('=', 1)) for item in alias]
            dups = [item for item, count in Counter([x[0] for x in alias]).items() if count > 1]
            if len(dups):
                raise FormatError(f"Duplicated @ALIAS ``{dups}`` in module ``{self.name}``")
            alias = dict(alias)
        else:
            alias = dict()
        # Handle alias
        for k1, k2 in list(alias.items()):
            # Currently group alias is list() / dict()
            groups = DSC_PACK_OP.search(k2)
            if groups:
                self.plugin.set_container(k1, groups.group(2), self.p)
                del alias[k1]
                continue
            if k2 in self.p:
                self.plugin.alias_map[k2] = k1
                del alias[k1]
        if len(alias):
            raise FormatError(f'Invalid @ALIAS for module ``{self.name}``:\n``{dict2str(alias)}``')

    @staticmethod
    def make_filter_statement(ft):
        ft = parse_filter(ft, dotted = False)[0]
        res = []
        variables = uniq_list(flatten_list([[ii[1][1] for ii in i] for i in ft]))
        for i in ft:
            tmp = []
            for ii in i:
                if len(ii[0]):
                    tmp.append(f'{ii[0]} (_{ii[1][1]} {ii[2]} {ii[3] if not ii[3] in variables else "_" + ii[3]})'.strip())
                else:
                    tmp.append(f'_{ii[1][1]} {ii[2]} {ii[3] if not ii[3] in variables else "_" + ii[3]}'.strip())
            res.append(f"({' and '.join(tmp)})")
        return ' or '.join(res)

    def apply_input_filter(self, ft):
        # first handle module specific filter
        ft = ft if ft else []
        if isinstance(ft, Mapping):
            valid = False
            for module in ft:
                if module == self.name or module == '?':
                    ft = ft[module]
                    valid = True
                    break
            if not valid:
                raise FormatError(f"Cannot find module ``{self.name}`` in @FILTER specification ``{list(ft.keys())}``.")
        if isinstance(ft, Mapping):
            raise FormatError(f"Invalid @FILTER format for module ``{self.name}`` (cannot be a key-value mapping).")
        # then generate filter from self.pg
        tmp = []
        for group in self.pg:
            for j in range(len(self.p[group[0]])):
                tmp.append(" AND ".join(["{} = {}".format(g, repr(self.p[g][j]) if isinstance(self.p[g][j], str) else self.p[g][j]) for g in group]))
        if len(tmp):
            ft.append(' OR '.join([f"({x})" for x in tmp]))
        if len(ft) == 0:
            return None
        # in case people use parentheses
        ft = flatten_list(ft)
        raw_rule = ft
        ft = self.make_filter_statement(ft)
        # Verify it
        statement = '\n'.join([f"{k} = {str(self.p[k])}" for k in self.p])
        value_str = ','.join([f'_{x}' for x in self.p.keys()])
        loop_str = ' '.join([f"for _{x} in {x}" for x in self.p])
        statement += f'\nret = len([({value_str}) {loop_str} if {ft}])'
        exec_env = dict()
        try:
            exec(statement, exec_env)
        except Exception:
            raise FormatError(f"Invalid @FILTER: ``{raw_rule}``!")
        if exec_env['ret'] == 0:
            raise FormatError(f"No parameter combination satisfies @FILTER ``{' AND '.join(raw_rule)}``!")
        return ft

    def apply_input_operator(self):
        '''
        Do the following:
        * convert string to raw string, leave alone `$` variables
        * strip off raw() operator
        * Handle file() parameter based on context
        '''
        raw_keys = []
        for k, p in list(self.p.items()):
            values = []
            for p1 in p:
                if isinstance(p1, str):
                    if p1.startswith('$') and len(p) > 1:
                        raise FormatError(f'Module input ``{k}`` cannot contain multiple elements ``{p}``')
                    if DSC_ASIS_OP.search(p1):
                        raw_keys.append(k)
                        p1 = DSC_ASIS_OP.search(p1).group(1)
                    elif DSC_FILE_OP.search(p1):
                        # p1 is file extension
                        file_ext = DSC_FILE_OP.search(p1).group(1).strip('.')
                        if k in self.rf:
                            # This file is to be saved as output
                            # FIXME: for multiple output case have to figure out what is the index of the output
                            self.plugin.add_input(k, '${_output:r}')
                            continue
                        else:
                            # This file is a temp file
                            self.plugin.add_tempfile(k, file_ext)
                            continue
                    else:
                        if not p1.startswith('$'):
                            p1 = repr(p1)
                if isinstance(p1, tuple):
                    # Supports nested tuples in R and Python
                    # But not in shell
                    p1 = self.plugin.format_tuple(self.format_tuple(p1))
                values.append(p1)
            if len(values) == 0:
                del self.p[k]
            else:
                self.p[k] = values
        for k in raw_keys:
            if k in self.p:
                self.p[k] = self.p.pop(k)

    def chop_input(self):
        '''
        Each of `self.p` is a list. Here we only keep the first item in that list
        '''
        for k in self.p:
            self.p[k] = [self.p[k][0]]

    @staticmethod
    def format_tuple(value):
        res = []
        # has_raw = False
        for v in value:
            if isinstance(v, tuple):
                res.append(format_tuple(v))
            elif isinstance(v, str):
                groups = DSC_ASIS_OP.search(v)
                if groups:
                    res.append(groups.group(1))
                    # has_raw = True
                else:
                    res.append(repr(v))
            else:
                res.append(str(v))
        return res

    def __str__(self):
        return dict2str(self.dump())

    def dump(self):
        return strip_dict(dict([('name', self.name),
                                ('dependencies', self.depends), ('command', '+'.join(self.exe['file'])),
                                ('input', self.p), ('input_filter', self.ft),
                                ('output_variables', self.rv),
                                ('output_files', self.rf),  ('shell_status', len(self.exe['path'])),
                                ('plugin_status', self.plugin.dump()),
                                ('runtime_options', dict([('exec_path', self.path),
                                                          ('workdir', self.workdir),
                                                          ('library_path', self.libpath)]))]),
                          mapping = dict, skip_keys = ['input'])


class DSC_Section:
    def __init__(self, content, sequence, output, replicate):
        self.content = content
        if 'run' not in self.content:
            if sequence is None:
                raise FormatError('Missing required ``DSC::run``.')
            else:
                self.content['run'] = []
        self.replicate = replicate if replicate else try_get_value(self.content, 'replicate')
        if not isinstance(self.replicate, int) or self.replicate <= 0:
            self.replicate = 1
        self.replicate = [x+1 for x in range(self.replicate)]
        self.output = output if output else try_get_value(self.content, 'output')
        if isinstance(self.output, list):
            self.output = self.output[0]
        self.OP = OperationParser()
        self.regularize_ensemble()
        # FIXME: check if sequence input is of the right type
        # and are valid modules
        self.groups = dict()
        self.concats = dict()
        self.sequence = []
        if isinstance(self.content['run'], Mapping):
            self.named_sequence = self.content['run']
        else:
            self.named_sequence = None
        if sequence is not None:
            for item in sequence:
                if isinstance(self.content['run'], Mapping) and item in self.content['run']:
                    self.sequence.extend(self.content['run'][item])
                else:
                    self.sequence.append(item)
        else:
            if isinstance(self.content['run'], Mapping):
                self.sequence = flatten_list(self.content['run'].values())
            else:
                self.sequence = self.content['run']
        self.sequence = [(x,) if isinstance(x, str) else x
                         for x in sum([self.OP(self.expand_ensemble(y)) for y in self.sequence], [])]
        self.sequence = filter_sublist(self.sequence)
        # FIXME: check if modules involved in sequence are indeed defined.
        self.sequence_ordering = self.__merge_sequences(self.sequence)
        self.options = dict()
        self.options['work_dir'] = self.content['work_dir'] if 'work_dir' in self.content else './'
        self.options['lib_path'] = self.content['lib_path'] if 'lib_path' in self.content else None
        self.options['exec_path'] = self.content['exec_path'] if 'exec_path' in self.content else None
        self.rlib = self.content['R_libs'] if 'R_libs' in self.content else []
        self.pymodule = self.content['python_modules'] if 'python_modules' in self.content else []

    @staticmethod
    def __merge_sequences(input_sequences):
        '''Extract the proper ordering of elements from multiple sequences'''
        # remove slicing
        sequences = [[y.split('[')[0] for y in x] for x in input_sequences]
        values = sequences[0]
        for idx in range(len(sequences) - 1):
            values = merge_lists(values, sequences[idx + 1])
        values = OrderedDict([(x, [-9]) for x in values])
        return values

    def regularize_ensemble(self):
        '''
        For definitions such as:
        ```
        preprocess: method1 * method2
        analyze: preprocess * (method3, method4)
        ```
        we will need to convert `analyze` into:
        analyze: method1 * method2 * (method3, method4)

        we also should handle exceptions here such that after this step,
        everything on the rhs should be whatever we've already have defined
        (but we can check this eventually after sequences have been generated)
        '''
        if 'define' not in self.content:
            return
        replace_list = []
        for lhs, rhs in self.content['define'].items():
            rhs = f"({', '.join(rhs)})"
            for item in reversed(replace_list):
                rhs =  re.sub(r"\b%s\b" % item[0], item[1], rhs)
            self.content['define'][lhs] = rhs
            replace_list.append((lhs, rhs))

    def expand_ensemble(self, value):
        '''
        input
        =====
        define:
            preprocess: filter * (norm1, norm2)
        run: data * preprocess * analyze

        where `define` is in self.content['define']
        `run` is in value

        output
        ======
        data * (filter * (norm1, norm2)) * analyze
        '''
        if 'define' not in self.content:
            return value
        for lhs, rhs in self.content["define"].items():
            if not '*' in rhs:
                # is a valid group
                # that is, only exists alternating modules not concatenate modules
                self.groups[lhs] = rhs.replace(',','').replace(')','').replace('(','').split()
            else:
                self.concats[lhs] = rhs.replace(',','').replace(')','').replace('(','').replace('*', '').split()
            # http://www.regular-expressions.info/wordboundaries.html
            value = re.sub(r"\b%s\b" % lhs, rhs, value)
        return value

    def check_looped_computation(self):
        # check duplicate modules in the same sequence
        for seq in self.sequence:
            if len(set(seq)) != len(seq):
                raise ValueError(f'Duplicated module found in DSC sequence ``{seq}``. '\
                                 'Iteratively executing modules is not yet supported.')

    def __str__(self):
        return dict2str(strip_dict(OrderedDict([('sequences to execute', self.sequence),
                                                ('sequence ordering', list(self.sequence_ordering.keys())),
                                                ('R libraries', self.rlib), ( 'Python modules', self.pymodule)]),
                                   mapping = OrderedDict))


class DSC_Pipeline:
    '''
    Analyzes DSC contents to determine dependencies and what exactly should be executed.
    It puts together DSC modules to sequences and continue to propagate computational routines for execution
    The output will be analyzed DSC ready to be translated to pipelines for execution
    '''
    def __init__(self, script_data):
        '''
        script_data comes from DSC_Script, having members:
        * modules
        * runtime (runtime.sequence is relevant)
        * output (output data prefix)
        Because different combinations of modules will lead to different
        I/O settings particularly with plugin status, here for each
        sequence, fresh deep copies of modules will be made from input modules

        Every module in a pipeline is a plugin, whether it be Python, R or Shell.
        When output contain variables the default output file format and method to save variables are
        applied.

        This class provides a member called `pipelines` which contains multiple pipelines
        '''
        self.pipelines = []
        for sequence in script_data.runtime.sequence:
            self.add_pipeline(sequence, script_data.modules, list(script_data.runtime.sequence_ordering.keys()))

    def add_pipeline(self, sequence, data, ordering):
        pipeline = OrderedDict()
        for name in sequence:
            module = copy.deepcopy(data[name])
            file_dependencies = []
            for k, p in list(module.p.items()):
                for p1_idx, p1 in enumerate(p):
                    if isinstance(p1, str):
                        if p1.startswith('$') and not (DSC_GVS.search(p1) or DSC_GV.search(p1)):
                            id_dependent = self.find_dependent(p1[1:], list(pipeline.values()),
                                                               module.name)
                            if id_dependent[1] not in module.depends:
                                module.depends.append(id_dependent[1])
                            if id_dependent[1][2] == 'var':
                                module.plugin.add_input(k, p1)
                            else:
                                # FIXME: for multiple output should figure out the index of previous output
                                file_dependencies.append((id_dependent[0], k))
                            # FIXME: should not delete, but rather transform it, when this
                            # can be properly bypassed on scripts
                            # module.p[k][p1_idx] = repr(p1)
                            module.p[k].pop(p1_idx)
                if len(module.p[k]) == 0:
                    del module.p[k]
            module.depends.sort(key = lambda x: ordering.index(x[0]))
            if len(file_dependencies):
                file_dependencies.sort()
                module.plugin.add_input([x[1] for x in file_dependencies], '${_input:r}')
            pipeline[module.name] = module
        # FIXME: ensure this does not happen
        # Otherwise will have to bring this back
        # self.check_duplicate_step(pipeline)
        self.pipelines.append(pipeline)

    @staticmethod
    def find_dependent(variable, pipeline, module_name):
        curr_idx = len(pipeline)
        if curr_idx == 0:
            raise FormatError('Pipeline variable ``$`` is not allowed in the input of the first module of a DSC sequence.')
        curr_idx = curr_idx - 1
        dependent = None
        while curr_idx >= 0:
            # Look up backwards for the corresponding block, looking at the output of the first step
            if variable in [x for x in pipeline[curr_idx].rv]:
                dependent = (pipeline[curr_idx].name, variable, 'var')
            if variable in [x for x in pipeline[curr_idx].rf]:
                if dependent is not None:
                    raise ValueError(f'[BUG]: ``{variable}`` cannot be both a variable and a file!')
                dependent = (pipeline[curr_idx].name, variable, 'file')
            if dependent is not None:
                break
            else:
                curr_idx = curr_idx - 1
        if dependent is None:
            raise FormatError(f'Cannot find output variable for ``${variable}`` in any of its upstream modules.'\
                              f' This variable is required by module ``{module_name}``.')
        return curr_idx, dependent

    def __str__(self):
        res = ''
        for idx, modules in enumerate(self.pipelines):
            res += f'# Pipeline {idx + 1}\n'
            res += f'## Modules\n' + '\n'.join(['### {x}\n```yaml\n{y}\n```\n' for x, y in modules.items()])
        return res


def remote_config_parser(host, paths):
    conf = None
    for h in [host, f'{host}.yml', f'{host}.yaml']:
        if os.path.isfile(h):
            conf = yaml.load(open(h).read())
    if conf is None:
        raise FormatError(f'Cannot find host configuration file ``{host}``.')
    if 'DSC' not in conf:
        raise FormatError(f'Cannot find required ``DSC`` remote configuration section, in file ``{host}``.')
    default = dict([('time_per_instance', '5m'), ('instances_per_job', 2), ('n_cpu', 1), ('mem_per_cpu', '2G'), ('trunk_workers', 1), ('queue', list(conf['DSC'].keys())[0])])
    if len(paths):
        default['prepend_path'] = paths
    if 'default' in conf:
        default.update(conf['default'])
    conf['default'] = default
    if conf['default']['queue'] not in conf['DSC']:
        raise FormatError(f"Cannot find configuration for queue ``{conf['default']['queue']}`` in ``DSC`` section of file ``{host}``.")
    for key in list(conf.keys()):
        if key == 'DSC':
            continue
        tmp = copy.deepcopy(default)
        tmp.update(conf[key])
        tmp['walltime'] = tmp.pop('time_per_instance')
        tmp['trunk_size'] = tmp.pop('instances_per_job')
        tmp['mem'] = tmp.pop('mem_per_cpu')
        tmp['cores'] = tmp.pop('n_cpu')
        keys = [k.strip() for k in key.split(',')]
        if len(keys) > 1:
            for k in keys:
                conf[k] = tmp
            del conf[key]
        else:
            conf[key] = tmp
    conf['DSC']['localhost'] = {'paths': {'home': '/Users/{user_name}' if platform.system() == 'Darwin' else '/home/{user_name}'}, 'address': 'localhost'}
    return conf
