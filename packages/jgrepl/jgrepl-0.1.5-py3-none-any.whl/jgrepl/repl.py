import os
import json
from collections import defaultdict

from cmd2 import Cmd

VERSION = '0.1.5'

class JSONRepl(Cmd):

    def __init__(self, filepath):
        self.allow_cli_args = False
        Cmd.__init__(self, use_ipython=True)
        self.filepath = filepath
        self._load_graph()
        self.intro = "JSON Graph REPL v.{}".format(VERSION)
        self._last_item = None


    def _load_graph(self):
        ''' Load the graph from a JSON file and pre-compute some helper 
        data structures for speedier access. '''
        self.poutput("*** Loading graph from '{}'...".format(self.filepath))
        with open(self.filepath) as json_file:
            self.graph = json.load(json_file)['graph']
        self._set_cwd('/')
        self._nodes = {}
        self._edges = {}
        self._children = defaultdict(set)
        self._parents = defaultdict(set)
        for edge in self.graph['edges']:
            self._children[edge['source'].upper()].add(edge['target'].upper())
            self._parents[edge['target'].upper()].add(edge['source'].upper())
            self._edges[(edge['source'].upper(), edge['target'].upper())] = edge
        for node in self.graph['nodes']:
            self._nodes[node['id'].upper()] = node
        self.root_nodes = [n['id'].upper() for n in self.graph['nodes'] 
                           if not self._parents[n['id'].upper()]]


    def _current_node_id(self):
        return self.cwd.split('/')[-1]


    def _children_for(self, node_id):
        if node_id:
            return self._children[node_id]
        return self.root_nodes


    def _current_children(self):
        return self._children_for(self._current_node_id())


    def _current_node(self):
        return self._nodes[self._current_node_id()]


    def _iter_paths_for(self, node_id, path=''):
        path = os.path.join(node_id, path) if path else node_id
        if not self._parents[node_id]:
            yield os.path.join('/', path)
        else:
            for parent_id in self._parents[node_id]:
                yield from self._iter_paths_for(parent_id, path=path)


    def _set_cwd(self, cwd):
        self.cwd = cwd
        self.prompt = "{}> ".format(self.cwd)


    def _parse_args(self, args_str):
        args = []
        opts = []
        for arg in args_str.split(' '):
            if arg.startswith('-'):
                arg = arg.strip('--').strip('-')
                opts.append(arg)
            else:
                args.append(arg)
        return args, opts


    def _match(self, node, attrs):
        matches = {}
        for attr, val in attrs.items():
            if (attr in node) and ((not val) or (str(node[attr]) == val)):
                matches[attr] = node[attr]
                continue
            data = node.get('metadata', {})
            if (attr in data) and ((not val) or (str(data[attr]) == val)):
                matches[attr] = data[attr]
                continue
            break
        else:
            return matches


    ################################
    # Generic command definitions:
    #

    def do_pwd(self, _args):
        ''' Print the current path '''
        self.poutput(self.cwd)


    def do_cd(self, args):
        ''' Change to a new path '''
        if args == '$':
            args = self._last_item or '/'

        if args.startswith('/'):
            self._set_cwd('/')
            args.strip('/')
 
        for component in args.upper().split('/'):
            if not component:
                continue
            if component == '..':
                self._set_cwd(os.path.abspath(os.path.join(self.cwd, '..')))
            else:
                if component in self._current_children():
                    self._set_cwd(os.path.join(self.cwd, component))
                else:
                    self.perror("Node not found: '{}'\n".format(component))


    def do_ls(self, args):
        ''' List all nodes under the current path '''
        args, opts = self._parse_args(args)
        current_children = {node_id: self._nodes[node_id] 
                            for node_id in self._current_children()}
        id_width = 1
        type_width = 1
        for node_id, node in current_children.items():
            id_width = max(id_width, len(node_id))
            type_width = max(type_width, len(node['type']))

        sorted_children = sorted(current_children.items(), 
                key=lambda n: n[1]['type'])

        for node_id, node in sorted_children:
            output_line = "{}".format(node_id)
            if 'l' in opts:
                node = self._nodes[node_id]
                output_line = '{0:<{id_width}} {1:<{type_width}} {2}'.format(
                        node_id, node['type'], node['label'], 
                        id_width=id_width, type_width=type_width)
            self.poutput(output_line)


    def do_info(self, args):
        ''' Print information about the current node '''
        args, opts = self._parse_args(args)
        node = self.graph
        if self.cwd == '/':
            self.poutput("CURRENT GRAPH: {} ('{}')".format(node.get('label', ''), self.filepath))
            self.poutput("GRAPH TYPE: {}".format(node.get('type')))
            self.poutput("NODES: {}".format(len(node['nodes'])))
            self.poutput("EDGES: {}".format(len(node['edges'])))
        else:
            node = self._current_node()
            self.poutput("NODE ID: {}".format(node['id']))
            self.poutput("NODE TYPE: {}".format(node['type']))
            self.poutput("NODE LABEL: {}".format(node.get('label', '')))
        meta_output = json.dumps(node.get('metadata', {}), indent=4)
        self.poutput(meta_output)


    def do_find(self, args):
        ''' Find all paths to a given node ID '''
        args, opts = self._parse_args(args)
        if args:
            search_id = args[0].upper()
            if search_id in self._nodes:
                for path in self._iter_paths_for(search_id):
                    self._last_item = path
                    self.poutput(path)


    def do_grep(self, args):
        '''
        Show IDs of nodes that match all of the supplied attributes. E.g:
        
          > grep node_type=food available_to

        shows all nodes of type 'food' that have an 'available_to' attribute 
        (regardless of its value)
        '''
        args, opts = self._parse_args(args)
        attrs = {}
        for arg in args:
            attr, _, val = arg.partition('=')
            attrs[attr] = val
        for node_id, node in self._nodes.items():
            matches = self._match(node, attrs)
            if matches:
                self.poutput(node_id)
                for attr, val in matches.items():
                    self.poutput("\t{} = {}".format(attr, val))
                self.poutput("")

    def do_explain(self, args):
        ''' Display the names of all nodes in the current path. '''
        components = self.cwd.split('/')
        prefix = ""
        for component in components:
            if component:
                self.poutput(prefix + self._nodes[component].get('label', component))
                prefix += '\t'
