import re, collections

class sv_natty:  
  cs = "/*"
  ce = "*/\n"
  nl = "\n"

  generic_prekeywords  = r"virtual|\blocal\b|protected|static|automatic|signed|unsigned"
  var_keywords         = r"enum|event|int|integer|shortint|longint|byte|bit|logic|reg|tri|string|real|shortreal|time|realtime"
  var_nd_types         = collections.OrderedDict([(r"localparam|parameter", "parameter"),
                                                  ("typedef"             , "typedef"  ), 
                                                  (var_keywords             , "var"      ), 
                                                  (r"covergroup"          , "cg"       )])
  method_keywords      = r"(function|task|property|sequence)"
  method_var_keywords  = r"(input|output|ref)"
  class_keywords       = r"class"
  class_extension      = r"extends"

  def do_nd(self, str):
    match = re.search(r"\b" + self.method_keywords + r"\b", str)
    if(match):
      return self.do_nd_methodz(str, match.group(1))
    else:
      match = re.search(r"(\b%s\b)" % self.class_keywords, str)
      if (match):
        return self.do_nd_class(str, match.group(1))
      else:
        return self.do_nd_varz   (str)

  def do_nd_methodz(self,str,method):
    iL = []
    oL = []
    rL = []
    match = re.search(r"(?P<ws>^ *)"+r"(?P<pre>.*)"+method+r" (?P<post>.*)\s*\((?P<varz>.*)\);", str)
    if (match):
      helper_dict = match.groupdict()
      ws          = " " * len(helper_dict["ws"])
      my_posts    = self.split_filter(helper_dict["post"])
      my_varz     = self.split_filter(helper_dict["varz"])
      nd_var      = ""
      var_group   = "input"
      print(my_posts)
      nd = ws + self.cs + method + ": " + my_posts[-1] + self.nl + self.nl
      print(my_varz)
      found_default = 0;
      for v in my_varz:
        #remove commas
        v = re.sub(r",", "", v)
        #see if this is a default
        if (v=="="):
            found_default = 1;
            continue
        if (found_default):
            found_default = 0
            continue
        match = re.search(self.method_var_keywords, v)
        if (match):
          var_group = match.group(1)
          continue
        if (var_group=="input"):
          iL.append(v)
        elif (var_group=="ref"):
          rL.append(v)
        elif (var_group=="output"):
          oL.append(v)
      issva = 0
      if method in ["property","sequence"]:
        issva = 1
      nd = self.method_var_nd(iL,"Input(s):"    ,nd,ws,issva)
      nd = self.method_var_nd(oL,"Output(s):"   ,nd,ws,issva)
      nd = self.method_var_nd(rL,"Reference(s):",nd,ws,issva)
      nd = nd[:-1] + self.ce
      return nd
    else:
      return ""    

  def method_var_nd(self,var_listz,listtype,nd, ws, issva):
    if (len(var_listz) != 0):
        vartype_listz = var_listz[0::2]
        if (issva==0):
          var_listz     = var_listz[1::2]
        nd += ws + listtype + self.nl
        my_ws = 0
        if (len(var_listz)!=0):
            my_ws = len(max(var_listz, key=len)) + 1
        idx = 0
        for v in var_listz:
            delta_ws = (my_ws - len(v))*" "
            nd += ws + "  " + v + delta_ws + "- " + ("<" + vartype_listz[idx] +"> " if (issva==0) else "") + self.nl
            idx = idx+1      
        return nd
    else:
        return nd

  def do_nd_varz(self,str):    
    #strip off all junk
    ws, str = self.strip_junk(str)
    #find any parameters
    my_param_list, str = self.look_4_param(str)
    #figure out the ND variable type comment
    my_var_list, nd_type, str = self.find_var_toungue_type(str)
    #implement the ND comment for variables for our programming language
    return self.implement_var_ND(my_param_list,my_var_list, nd_type, ws, str)

  def look_4_param(self, str):
    match = re.search(r"(#.*\))", str)
    my_param = ""
    my_param_list = []
    my_clean_param_list = []
    if (match):
        my_param = re.sub(r"(#|\(|\)|\s)+", "", match.group(1))
        str      = re.sub(r"#.*\)", "", str)
        my_param_list = self.split_filter(my_param, ',')
        default_found = 0
        for i in my_param_list:
            if (i=="="):
                default_found = 1
                continue
            if (default_found):
                default_found = 0
                continue
            my_clean_param_list.append(i)
            print(my_clean_param_list)
    return my_clean_param_list, str

  def strip_junk(self,str):
    regex_start_2_word = r"(^ *)\b"
    match = re.search(regex_start_2_word, str)
    ws = len(match.group(1)) * " "
    str = re.sub(regex_start_2_word, "", str)
    str = re.sub(r"(%s)+" % self.generic_prekeywords, "", str)
    str = re.sub(r"(;|\[.*\]|=.*;$)+", "", str)
    return ws, str

  def find_var_toungue_type(self,str):
    nd_type = ""
    for k in self.var_nd_types:
        print(k)
        match = re.search(k, str)
        if (match):
            str = re.sub(k, "", str)
            nd_type = self.var_nd_types[k]
            break
    if (nd_type==""):
      nd_type = "obj"
    my_var_list = re.split(" ", str)
    my_var_list = list(filter(None, my_var_list))
    return my_var_list, nd_type, str

  def implement_var_ND(self,my_param_list,my_var_list, nd_type, ws, str):
    nd_param      = ""
    if (len(my_param_list)!=0):
        nd_param = ws + "Parameter(s):" + self.nl
        for i in my_param_list:
            nd_param += ws + "  " + i + " - " + self.nl
    nd = ws + self.cs + nd_type + ": " + my_var_list[-1] + self.nl + nd_param + ws + ("<"+my_var_list[-2]+">" if (nd_type=="obj") else "") + self.ce
    return nd

  def split_filter(self, splitme, delim=' ', filt=None):
    return list(filter(filt, re.split(delim, splitme)))

  def do_nd_class(self, str, class_type):
    ws, str = self.strip_junk(str)
    str = re.sub(self.class_extension + ".*$","",str)
    my_param_list, str = self.look_4_param(str)
    match = re.search(class_type+r" *(\w+)", str)
    name = ""
    if (match):
        name = match.group(1)
    nd = ws + self.cs + class_type + ": " + name + self.nl
    if (len(my_param_list) != 0):
        nd += ws + "Parameter(s)" + self.nl
        for i in my_param_list:
            nd += ws + "  " + i + " - " + self.nl
    nd = nd[:-1] + self.ce
    return nd


    


