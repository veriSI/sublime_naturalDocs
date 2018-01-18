import sublime, sublime_plugin, re 
from .sv_natty import sv_natty

my_tounges = {"sv|svp|svh":"system-verilog", "^v$|^vh$":"verilog", "vhdl": "vhdl", "c|cpp":"C/C++","py|py2|py3":"Python"}

class ndCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    fn = self.view.file_name()
    #path remover
    fn = re.sub(r"(.*\\)+|(.*/)+","",fn)
    match = re.search(r"(.*)\.(.*)",fn)
    if (match):
      ext = match.group(2)
    #determine file type
    tounge_found = 0
    file_type    =""
    for key in my_tounges:
      match = re.search(r"^%s$" % key, ext)
      if (match):
      	file_type = my_tounges[key]
      	tounge_found = 1
    if (file_type=="system-verilog"):
      x = sv_natty()
      for region in self.view.sel():
        line = self.view.line(region)
        line_contents = self.view.substr(line)
        nd = x.do_nd(line_contents)
        if (len(nd)>0 ):
          self.view.insert(edit, line.a, nd)