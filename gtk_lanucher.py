#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:     fifa .big archive explorer and extractor
#
# Author:      gregkwaste
#
# Created:     21/09/2014
# Copyright:   (c) gregkwaste 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import gtk,struct,os,zlib,webbrowser



#FUNCTIONS
def read_string(f):
    c=''
    for i in range(128):
        s = struct.unpack('<B', f.read(1))[0]
        if s == 0:
            return c
        c += chr(s)

    return {'FINISHED'}


def rec_tree(iter,mps,index,data,path,tree,hist):
    if index==len(mps)-1:
        hist[index][mps[index]]=tree.append(iter,[mps[index],data[0],data[1],data[2],data[3],data[4]])

    else:
        try:
            nextiter=hist[index][mps[index]]
        except:
            nextiter=tree.append(iter,[mps[index],0,0,'','dir',0])
            hist[index][mps[index]]=nextiter

        index+=1
        rec_tree(nextiter, mps, index, data, path, tree, hist)


class FileChooserWindow(gtk.Window):

    def __init__(self):
        self.path = ''
        self.fcd = gtk.FileChooserDialog("Select Big File", None, gtk.FILE_CHOOSER_ACTION_OPEN,
               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        self.response = self.fcd.run()
        if self.response==gtk.RESPONSE_OK:
            self.path = self.fcd.get_filename()
            print("Selected File: " + self.fcd.get_filename())
            self.fcd.destroy()
        elif self.response == gtk.RESPONSE_CANCEL:
            print("Closing File Dialog")
            self.fcd.destroy()




class AppWindow:
    def __init__(self):
        self.gladefile = "layout.glade"
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("window")
        self.window.connect("delete-event", self.on_window_destroy)
        self.tree = self.builder.get_object("treestore")
        self.treeview = self.builder.get_object("treeview1")
        self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.status_label = self.builder.get_object("status_label")
        self.about_win = self.builder.get_object("about")
        #Context Menu Definition
        self.context_menu=gtk.Menu()

        item=gtk.MenuItem("Export Packed")
        self.context_menu.append(item)
        item.connect("activate",self.menu_item_response,"packed_export")
        item.show()

        item=gtk.MenuItem("Export Unpacked")
        self.context_menu.append(item)
        item.connect("activate",self.menu_item_response,"unpacked_export")
        item.show()

        item=gtk.MenuItem("Expand All")
        self.context_menu.append(item)
        item.connect("activate",self.menu_item_response,"expand_all")
        item.show()

        item=gtk.MenuItem("Colapse All")
        self.context_menu.append(item)
        item.connect("activate",self.menu_item_response,"collapse_all")
        item.show()

        item=gtk.MenuItem("Select Children")
        self.context_menu.append(item)
        item.connect("activate",self.menu_item_response,"select_children")
        item.show()




        #excplicit signal connections
        item=self.builder.get_object("pack_export")
        item.connect("activate",self.menu_item_response,"packed_export")
        item=self.builder.get_object("unpack_export")
        item.connect("activate",self.menu_item_response,"unpacked_export")

        #initialize file dictionary
        self.hist=[]
        self.hist[0:7]={},{},{},{},{},{},{},{}


    def clear_hist(self):
        self.hist[0:7]={},{},{},{},{},{},{},{}

    def menu_item_response(self,widget,mode):
        (model,pathlist)=self.treeview.get_selection().get_selected_rows()
        f=open(self.active_file.path,'rb')
        if mode=="packed_export":
            print('I am exporting packed')

            for path in pathlist:
                tree_iter=model.get_iter(path)
                off=model.get_value(tree_iter,1)
                size=model.get_value(tree_iter,2)
                path=model.get_value(tree_iter,3)
                f.seek(off)
                if path=='': continue
                path='C:'+path
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
                #print(path,off,size)
                t=open(path,'wb')
                t.write(f.read(size))
                t.close()

            self.status_label.set_label("Exported "+str(len(pathlist))+" Files")
            print("Export Successfull")
            f.close()
        elif mode=="unpacked_export":
            print('I am exporting unpacked')
            for path in pathlist:
                tree_iter=model.get_iter(path)
                off=model.get_value(tree_iter,1)
                size=model.get_value(tree_iter,2)
                path=model.get_value(tree_iter,3)
                f.seek(off)
                if path=='': continue
                path='C:'+path
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))

                t=open(path,'wb')
                if str(f.read(8))=='chunkzip':
                    #print('chunkzip')
                    f.read(12)
                    sec_num=struct.unpack('>I',f.read(4))[0]
                    f.read(8)
                    for i in range(sec_num):
                        #Uniform the offset
                        off=f.tell() % 4
                        if off:
                            f.read(4-off)
                        #find sec length
                        sec_found=False
                        while sec_found==False:
                           sec_len=struct.unpack('>I',f.read(4))[0]
                           if not sec_len==0:
                              sec_found=True
                        f.read(4) #Skip 00 00 00 01
                        data=f.read(sec_len)  #Store part
                        try:
                            t.write(zlib.decompress(data,-15))
                        except zlib.error:
                            print 'corrupt_file, skipping'
                            continue
                else:
                    t.write(f.read(size))
                t.close()
            self.status_label.set_label("Exported "+str(len(pathlist))+" Files")
            print("Export Successfull")
            f.close()
        elif mode=="expand_all":
            self.treeview.expand_all()
        elif mode=="collapse_all":
            self.treeview.collapse_all()
        elif mode=="select_children":
            treeselection = self.treeview.get_selection()
            (model, pathlist) = treeselection.get_selected_rows()
            for path in pathlist:
                iter=model.get_iter(path)
                for i in range(model.iter_n_children(iter)):
                    treeselection.select_iter(model.iter_nth_child(iter,i))
                treeselection.unselect_iter(iter)


    def open_file(self,event):
        self.clear_hist()
        self.tree.clear()
        self.active_file=FileChooserWindow()
        self.status_label.set_label("Reading .big file")
        num=self.load_big()
        print("Total Files Detected: ",num)


    def about_win(self,event):
        response=self.about_win.run()
        if response == gtk.RESPONSE_DELETE_EVENT or response == gtk.RESPONSE_CANCEL:
            self.about_win.hide()

    def visit_url(self,widget):
        webbrowser.open(widget.get_uri())

    def on_window_destroy(self, *args):
        self.window.destroy()
        gtk.main_quit(*args)

    def on_button1_pressed(self,button):
        print("Button Clicked")

    def on_treeview1_button_press_event(self,widget,event):
        if event.button==3 and self.treeview.get_selection().count_selected_rows():

            self.context_menu.popup(None,None,None,event.button,event.time)

    def load_big(self):
        chooser,tree,hist,status=self.active_file,self.tree,self.hist,self.status_label
        #prog.set_fraction(0.0)
        #print(chooser.path)
        if chooser.path:
            f=open(chooser.path,'rb')
        else:
            return 0
        #Parse big header
        while gtk.events_pending():
            gtk.main_iteration()
        header=f.read(4)
        full_size=struct.unpack('>I',f.read(4))[0]
        file_count=struct.unpack('>I',f.read(4))[0]
        def_size=struct.unpack('>I',f.read(4))[0]
        #prog.set_pulse_step=round(1/file_count,5)
        #prog.set_pulse_step=1
        data_list=[] #storing file data
        for i in range(file_count):
            data=[]
            data.append(struct.unpack('>2I',f.read(8)))#0
            data_name=read_string(f)
            mps=data_name.split("/")
            #print(mps)
            data_path=''
            for name in mps:
                data_path+='\\'+name
            data.append((mps,data_path))#1
            #print(data)
            data_list.append(data)
        for i in range(file_count): #getting data types
            f.seek(data_list[i][0][0])
            head=struct.unpack('>I',f.read(4))[0]
            if head==1161909062:
                head='EASF'
                chunk_size=struct.unpack('>I',f.read(4))[0]
            else:
                head='Chunkzip'
                chunk_size=data_list[i][0][1]
            data_list[i].append((head,chunk_size))#2
        for i in range(file_count): #storing in the tree
            data_off=data_list[i][0][0]
            data_size=data_list[i][0][1]
            mps=data_list[i][1][0]
            data_path=data_list[i][1][1]
            head=data_list[i][2][0]
            chunk_size=data_list[i][2][1]

            iter=None

            rec_tree(iter,mps,0,(data_off,data_size,data_path,head,hex(chunk_size)),'',tree,hist)
            #prog.set_fraction(round(float(i)/float(file_count),2))
            #prog.set_text(str(prog.get_fraction()*float(100))+"%")
            #while gtk.events_pending():
            #    gtk.main_iteration()
            #print('done')
        #prog.set_fraction(1)
        status.set_label(str(file_count) +" Files Detected")
        f.close()
        return file_count




app=AppWindow()
app.window.show_all()
gtk.main()







