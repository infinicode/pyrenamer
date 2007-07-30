# -*- coding: utf-8 -*-

"""
Copyright (C) 2006-2007 Adolfo González Blázquez <code@infinicode.org>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version. 

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details. 

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

If you find any bugs or have any suggestions email: code@infinicode.org
"""

try:
    import gtk
    import gtk.glade
    import gobject
except:
    raise SystemExit


import pygtk
if gtk.pygtk_version < (2, 0):
      print "PyGtk 2.0 or later required for this app to run"
      raise SystemExit

  
try:
    import gconf
    HAS_GCONF = True
except:
    HAS_GCONF = False


import treefilebrowser
import pyrenamerfilefuncs as renamerfilefuncs
import pyrenamer_globals as pyrenamerglob
import tooltips

import threading
import os

import locale
import gettext

from gettext import gettext as _
gettext.bindtextdomain(pyrenamerglob.name, pyrenamerglob.locale_dir)
gettext.textdomain(pyrenamerglob.name)
gtk.glade.bindtextdomain(pyrenamerglob.name, pyrenamerglob.locale_dir)
gtk.glade.textdomain(pyrenamerglob.name)

class pyRenamer:
    
    def __init__(self):
    
    	global HAS_GCONF
        
        # Vars
        self.home = os.environ["HOME"]
        self.current_dir = self.home
        self.window_maximized = False
        self.count = 0
        self.populate_id = []
        self.window_width = 1
        self.window_height = 1
        self.window_posx = 0
        self.window_posy = 0
        self.listing = []
        self.listing_thread = None
        
        # Gconf preferences stuff
        self.gconf_path = '/apps/' + pyrenamerglob.name
        self.gconf_key_dir = self.gconf_path + '/dir'
        self.gconf_window_maximized = self.gconf_path + '/window_maximized'
        self.gconf_pane_position = self.gconf_path + '/pane_position'
        self.gconf_window_width = self.gconf_path + '/window_width'
        self.gconf_window_height = self.gconf_path + '/window_height'
        self.gconf_window_posx = self.gconf_path + '/window_posx'
        self.gconf_window_posy = self.gconf_path + '/window_posy'
        
        # Init Glade stuff
        self.glade_tree = gtk.glade.XML(pyrenamerglob.gladefile, "main_window")
        
        # Get some widgets
        self.main_window = self.glade_tree.get_widget("main_window")
        self.main_hpaned = self.glade_tree.get_widget("main_hpaned")
        self.selected_files, selected_files_scrolled = self.create_selected_files_treeview()
        self.file_pattern = self.glade_tree.get_widget("file_pattern")
        self.add_recursive = self.glade_tree.get_widget("add_recursive")
        self.original_pattern = self.glade_tree.get_widget("original_pattern")
        self.renamed_pattern = self.glade_tree.get_widget("renamed_pattern")
        self.statusbar = self.glade_tree.get_widget("statusbar")
        self.notebook = self.glade_tree.get_widget("notebook")
        self.rename_button = self.glade_tree.get_widget("rename_button")
        self.subs_spaces = self.glade_tree.get_widget("subs_spaces")
        self.subs_capitalization = self.glade_tree.get_widget("subs_capitalization")
        self.subs_spaces_combo = self.glade_tree.get_widget("subs_spaces_combo")
        self.subs_capitalization_combo = self.glade_tree.get_widget("subs_capitalization_combo")
        self.subs_replace = self.glade_tree.get_widget("subs_replace")
        self.subs_replace_orig = self.glade_tree.get_widget("subs_replace_orig")
        self.subs_replace_new = self.glade_tree.get_widget("subs_replace_new")
        self.subs_replace_label = self.glade_tree.get_widget("subs_replace_label")
        self.subs_accents = self.glade_tree.get_widget("subs_accents")
        self.insert_radio = self.glade_tree.get_widget("insert_radio")
        self.insert_entry = self.glade_tree.get_widget("insert_entry")
        self.insert_pos = self.glade_tree.get_widget("insert_pos")
        self.insert_end = self.glade_tree.get_widget("insert_end")
        self.delete_radio = self.glade_tree.get_widget("delete_radio")
        self.delete_from = self.glade_tree.get_widget("delete_from")
        self.delete_to = self.glade_tree.get_widget("delete_to")
        self.manual = self.glade_tree.get_widget("manual")
        self.menu_rename = self.glade_tree.get_widget("menu_rename")
        self.images_original_pattern = self.glade_tree.get_widget("images_original_pattern")
        self.images_renamed_pattern = self.glade_tree.get_widget("images_renamed_pattern")
        self.music_original_pattern = self.glade_tree.get_widget("music_original_pattern")
        self.music_renamed_pattern = self.glade_tree.get_widget("music_renamed_pattern")
        
        self.statusbar_context = self.statusbar.get_context_id("file_renamer")
        
        # Get Glade defined signals
        signals = { "on_main_window_destroy": self.on_main_quit,
                    "on_main_window_window_state_event": self.on_main_window_window_state_event,
                    "on_main_window_configure_event": self.on_main_window_configure_event,
                    "on_file_pattern_changed": self.on_file_pattern_changed,
                    "on_original_pattern_changed": self.on_original_pattern_changed,
                    "on_renamed_pattern_changed": self.on_renamed_pattern_changed,
                    "on_add_recursive_toggled": self.on_add_recursive_toggled,
                    "on_preview_button_clicked": self.on_preview_button_clicked,
                    "on_rename_button_clicked": self.on_rename_button_clicked,
                    "on_exit_button_clicked": self.on_main_quit,
                    "on_menu_preview_activate": self.on_preview_button_clicked,
                    "on_menu_rename_activate": self.on_rename_button_clicked,
                    "on_subs_spaces_toggled": self.on_subs_spaces_toggled,
                    "on_subs_capitalization_toggled": self.on_subs_capitalization_toggled,
                    "on_subs_spaces_combo_changed": self.on_subs_spaces_combo_changed,
                    "on_subs_capitalization_combo_changed": self.on_subs_capitalization_combo_changed,
                    "on_subs_replace_toggled": self.on_subs_replace_toggled,
                    "on_subs_replace_orig_changed": self.on_subs_replace_orig_changed,
                    "on_subs_replace_new_changed": self.on_subs_replace_new_changed,
                    "on_subs_accents_toggled": self.on_subs_accents_toggled,
                    "on_insert_radio_toggled": self.on_insert_radio_toggled,
                    "on_insert_entry_changed": self.on_insert_entry_changed,
                    "on_insert_pos_changed": self.on_insert_pos_changed,
                    "on_insert_end_toggled": self.on_insert_end_toggled,
                    "on_delete_radio_toggled": self.on_delete_radio_toggled,
                    "on_delete_from_changed": self.on_delete_from_changed,
                    "on_delete_to_changed": self.on_delete_to_changed,
                    "on_images_original_pattern_changed": self.on_images_original_pattern_changed,
                    "on_images_renamed_pattern_changed": self.on_images_renamed_pattern_changed,
                    "on_music_original_pattern_changed": self.on_music_original_pattern_changed,
                    "on_music_renamed_pattern_changed": self.on_music_renamed_pattern_changed,
                    "on_menu_quit_activate": self.on_main_quit,
                    "on_menu_about_activate": self.about_info,
                    "on_notebook_switch_page": self.on_notebook_switch_page,
                    "on_cut_activate": self.on_cut_activate,
                    "on_copy_activate": self.on_copy_activate,
                    "on_paste_activate": self.on_paste_activate,
                    "on_clear_activate": self.on_clear_activate,
                    "on_select_all_activate": self.on_select_all_activate,
                    "on_select_nothing_activate": self.on_select_nothing_activate,
                    "on_quit_button_clicked": self.on_main_quit }
        self.glade_tree.signal_autoconnect(signals)
        
        # Create ProgressBar and add it to the StatusBar. Add also a Stop icon
        self.progressbar = gtk.ProgressBar()
        self.progressbar.set_pulse_step(0.01)
        
        self.stop_button = gtk.Button()
        self.stop_button.set_relief(gtk.RELIEF_NONE)
        
        stop_image = gtk.Image()
        stop_image.set_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_MENU)
        stop_image.set_size_request(12,12)
        
        self.stop_button.connect("clicked", self.on_stop_button_clicked)
        self.stop_button.set_image(stop_image)
        self.stop_button.set_size_request(24,12)
        
        self.statusbar.pack_start(self.stop_button,0,0)
        self.statusbar.pack_start(self.progressbar,0,0)
        #self.statusbar.set_size_request(24,24)
        self.statusbar.show_all()
        self.stop_button.hide()
               
        # Init TreeFileBrowser
        self.file_browser = treefilebrowser.TreeFileBrowser()
        self.file_browser_view = self.file_browser.get_view()
        file_browser_scrolled = self.file_browser.get_scrolled()
        self.file_browser.connect("cursor-changed", self.dir_selected)

        # Add dirs and files tomain window
        self.main_hpaned.pack1(file_browser_scrolled, resize=True, shrink=False)
        self.main_hpaned.pack2(selected_files_scrolled, resize=True, shrink=False)
                
        # Create model and add dirs
        self.create_model()
        
        #  Set cursor on selected dir
        self.file_browser.set_active_dir(self.current_dir)
        
        # Init comboboxes
        self.subs_spaces_combo.set_active(0)
        self.subs_capitalization_combo.set_active(0)
        
        # Init menu items, some widgets and window name
        self.menu_rename.set_sensitive(False)
        self.main_window.set_title(pyrenamerglob.name_long)
        self.main_window.set_icon_from_file(pyrenamerglob.icon)
        self.delete_from.set_sensitive(False)
        self.delete_to.set_sensitive(False)
        
        # Read preferences using Gconf
        if HAS_GCONF: self.preferences_read()
        
        # Init tooltips
        tips = tooltips.ToolTips(self.column_preview)
        tips.add_view(self.selected_files)
        
        # Hide music tab if necessary
        if not pyrenamerglob.have_eyed3:
            self.notebook.get_nth_page(5).hide()
    


#---------------------------------------------------------------------------------------
# Model and View stuff

    def create_selected_files_treeview(self):
    	""" Create the TreeView and the ScrolledWindow for the selected files """
        view = gtk.TreeView()
        view.set_headers_visible(True)
        view.set_enable_search(True)
        view.set_reorderable(False)
        view.set_rules_hint(True)
        view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        view.connect("cursor-changed", self.on_selected_files_cursor_changed)
    
        # Create scrollbars around the view
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scrolled.add(view)
        scrolled.show()
        
        return view, scrolled


    def create_model(self):
    	""" Create the model to hold the needed data
        Model = [file, /path/to/file, newfilename, /path/to/newfilename] """
        self.file_selected_model = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.selected_files.set_model(self.file_selected_model)
        
        renderer1 = gtk.CellRendererText()
        column1 = gtk.TreeViewColumn(_("Original file name"), renderer1, text=0)
        #column1.set_resizable(True)
        self.selected_files.append_column(column1)

        renderer2 = gtk.CellRendererText()
        column2 = gtk.TreeViewColumn(_("Renamed file name"), renderer2, text=2)
        self.column_preview = column2
        #column2.set_resizable(True)
        self.selected_files.append_column(column2)

        self.selected_files.show()
    
    
    def rename_rows(self, model, path, iter, user_data):
    	""" This function is called by foreach to rename files on every row """
    	ori = model.get_value(iter, 1)
    	new = model.get_value(iter, 3)
        
        if new != None and new != '':
            result = renamerfilefuncs.rename_file(ori, new)
            if not result: self.display_error_dialog(_("Could not rename file %s to %s") % (ori, new))


    def preview_rename_rows(self, model, path, iter, paths):
    	""" Called when Preview button is clicked.
    	Get new names and paths and add it to the model """
        
        if (paths != None) and (path not in paths) and (paths != []) and self.notebook.get_current_page() != 3:
            # Preview only selected rows (if we're not on manual rename)
            model.set_value(iter, 2, None)
            model.set_value(iter, 3, None)
            return
        
        # Get current values
        name = model.get_value(iter, 0)
        path = model.get_value(iter, 1)
        newname = name
        newpath = path
        
        if self.notebook.get_current_page() == 0:
            # Replace using patterns
            pattern_ini = self.original_pattern.get_text()
            pattern_end = self.renamed_pattern.get_text()
            newname, newpath = renamerfilefuncs.rename_using_patterns(name, path, pattern_ini, pattern_end, self.count)
        
        elif self.notebook.get_current_page() == 1:
            # Replace orig with new
            if self.subs_replace.get_active() and newname != None:
                orig = self.subs_replace_orig.get_text()
                new = self.subs_replace_new.get_text()
                newname, newpath = renamerfilefuncs.replace_with(newname, newpath, orig, new)
            
            # Replace spaces
            if self.subs_spaces.get_active() and newname != None:
                newname, newpath = renamerfilefuncs.replace_spaces(newname, newpath, self.subs_spaces_combo.get_active())
            
            # Replace capitalization
            if self.subs_capitalization.get_active() and newname != None:
                newname, newpath = renamerfilefuncs.replace_capitalization(newname, newpath, self.subs_capitalization_combo.get_active())
                
            # Replace accents
            if self.subs_accents.get_active() and newname != None:
                newname, newpath = renamerfilefuncs.replace_accents(newname, newpath)
        
        elif self.notebook.get_current_page() == 2:
            # Insert / delete
            if self.insert_radio.get_active():
                text = self.insert_entry.get_text()
                if text != "":
                    if self.insert_end.get_active():
                        pos = None
                    else:
                        pos = int(self.insert_pos.get_value())-1
                    newname, newpath = renamerfilefuncs.insert_at(newname, newpath, text, pos)
            elif self.delete_radio.get_active():
                ini = int(self.delete_from.get_value())-1
                to = int(self.delete_to.get_value())-1
                newname, newpath = renamerfilefuncs.delete_from(newname, newpath, ini, to)
                
        elif self.notebook.get_current_page() == 3:
            # Manual rename
            nmodel, niter = self.selected_files.get_selection().get_selected()
            if niter != None:
                if nmodel.get_value(niter,0) == name:
                    newname = self.manual.get_text()
                    newpath = renamerfilefuncs.get_new_path(newname, path)
                else:
                    newname = model.get_value(iter, 2)
                    newpath = model.get_value(iter, 3)
        
        elif self.notebook.get_current_page() == 4:
            # Replace images using patterns
            pattern_ini = self.images_original_pattern.get_text()
            pattern_end = self.images_renamed_pattern.get_text()
            newname, newpath = renamerfilefuncs.rename_using_patterns(name, path, pattern_ini, pattern_end, self.count)
            newname, newpath = renamerfilefuncs.replace_images(name, path, newname, newpath)
            
        elif self.notebook.get_current_page() == 5 and pyrenamerglob.have_eyed3:
            # Replace music using patterns
            pattern_ini = self.music_original_pattern.get_text()
            pattern_end = self.music_renamed_pattern.get_text()
            newname, newpath = renamerfilefuncs.rename_using_patterns(name, path, pattern_ini, pattern_end, self.count)
            newname, newpath = renamerfilefuncs.replace_music(name, path, newname, newpath)
        
        
        # Set new values on model
        if newname != '' and newname != None:
            model.set_value(iter, 2, newname)
            model.set_value(iter, 3, newpath)
        else:
            model.set_value(iter, 2, None)
            model.set_value(iter, 3, None)
        self.count += 1
        

#---------------------------------------------------------------------------------------
# Callbacks

    def on_selected_files_cursor_changed(self, treeview):
        """ Clicked a file """
        
        if self.notebook.get_current_page() == 3:
            model, iter = treeview.get_selection().get_selected()
            name = model.get_value(iter,0)
            self.manual.set_text(name)


    def on_stop_button_clicked(self, widget):
    	""" The stop button on Statusbar.
    	Stop adding items to the selected files list and show information on statusbar """
    	self.populate_stop()
        
    
    def on_main_window_window_state_event(self, window, event):
    	""" Thrown when window is maximized or demaximized """
        if event.changed_mask & gtk.gdk.WINDOW_STATE_MAXIMIZED:
            if event.new_window_state & gtk.gdk.WINDOW_STATE_MAXIMIZED:
                self.window_maximized = True
                self.statusbar.set_has_resize_grip(False)
            else:
                self.window_maximized = False
                self.statusbar.set_has_resize_grip(True)


    def on_main_window_configure_event(self, window, event):
        """ Saving window size to avoid losing data when it gets destroyed """
        self.window_width, self.window_height = self.main_window.get_size()
        self.window_posx, self.window_posy = self.main_window.get_position()

    
    def on_rename_button_clicked(self, widget):
    	""" For everyrow rename the files as requested """
        
        self.file_selected_model.foreach(self.rename_rows, None)
        self.dir_reload_current()
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)


    def on_preview_button_clicked(self, widget):
    	""" Set the item count to zero and get new names and paths for files on model """
        self.count = 0
            
        # Get selected rows and execute rename function
        model, paths = self.selected_files.get_selection().get_selected_rows()
        self.file_selected_model.foreach(self.preview_rename_rows, paths)
        
        self.selected_files.columns_autosize()
        self.rename_button.set_sensitive(True)
        self.menu_rename.set_sensitive(True)


    def on_add_recursive_toggled(self, widget):
    	""" Reload current dir, but with Recursive flag enabled """
        self.dir_reload_current()


    def on_file_pattern_changed(self, widget):
    	""" Reload the current dir 'cause we need it """
        self.dir_reload_current()


    def on_original_pattern_changed(self, widget):
    	""" Reload current dir and disable Rename button """
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)


    def on_renamed_pattern_changed(self, widget):
    	""" Disable Rename button (user has to click on Preview again) """
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)
        
    
    def on_subs_spaces_toggled(self, widget):
    	""" Enable/Disable spaces combo """
    	self.subs_spaces_combo.set_sensitive(widget.get_active())
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)
    	
        
    def on_subs_capitalization_toggled(self, widget):
    	""" Enable/Disable caps combo """
    	self.subs_capitalization_combo.set_sensitive(widget.get_active())
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)
    

    def on_subs_replace_toggled(self, widget):
        """ Enable/Disable replace with text entries """
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)
        self.subs_replace_new.set_sensitive(widget.get_active())
        self.subs_replace_orig.set_sensitive(widget.get_active())
        self.subs_replace_label.set_sensitive(widget.get_active())
        
    
    def on_subs_spaces_combo_changed(self, widget):
    	""" Disable Rename button (user has to click on Preview again) """
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)
        
        
    def on_subs_capitalization_combo_changed(self, widget):
    	""" Disable Rename button (user has to click on Preview again) """
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)
        
    
    def on_subs_replace_orig_changed(self, widget):
        """ Disable Rename button (user has to click on Preview again) """
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)


    def on_subs_replace_new_changed(self, widget):
        """ Disable Rename button (user has to click on Preview again) """
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)
        
    
    def on_subs_accents_toggled(self, widget):
        """ Enable/Disable accents """
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)
        

    def on_insert_radio_toggled(self, widget):
        """ Disable Rename button (user has to click on Preview again) """
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)
        self.insert_entry.set_sensitive(True)
        self.insert_pos.set_sensitive(True)
        self.insert_end.set_sensitive(True)
        self.delete_from.set_sensitive(False)
        self.delete_to.set_sensitive(False)
        
        
    def on_insert_entry_changed(self, widget):
        """ Disable Rename button (user has to click on Preview again) """
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)
        
        
    def on_insert_pos_changed(self, widget):
        """ Disable Rename button (user has to click on Preview again) """
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)
        
        
    def on_insert_end_toggled(self, widget):
        """ Disable Rename button (user has to click on Preview again) """
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)
        self.insert_pos.set_sensitive(not self.insert_end.get_active())
        
        
    def on_delete_radio_toggled(self, widget):
        """ Disable Rename button (user has to click on Preview again) """
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)
        self.delete_from.set_sensitive(True)
        self.delete_to.set_sensitive(True)
        self.insert_entry.set_sensitive(False)
        self.insert_pos.set_sensitive(False)
        self.insert_end.set_sensitive(False)
        
        
    def on_delete_from_changed(self, widget):
        """ Disable Rename button (user has to click on Preview again) """
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)
        if self.delete_from.get_value() > self.delete_to.get_value(): 
            self.delete_from.set_value(self.delete_to.get_value())
        
        
    def on_delete_to_changed(self, widget):
        """ Disable Rename button (user has to click on Preview again) """
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)
        if self.delete_to.get_value() < self.delete_from.get_value(): 
            self.delete_to.set_value(self.delete_from.get_value())

    def on_images_original_pattern_changed(self, widget):
        """ Reload current dir and disable Rename button """
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)


    def on_images_renamed_pattern_changed(self, widget):
        """ Disable Rename button (user has to click on Preview again) """
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)


    def on_music_original_pattern_changed(self, widget):
        """ Reload current dir and disable Rename button """
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)


    def on_music_renamed_pattern_changed(self, widget):
        """ Disable Rename button (user has to click on Preview again) """
        self.rename_button.set_sensitive(False)
        self.menu_rename.set_sensitive(False)


    def on_notebook_switch_page(self, notebook, page, page_num):
        """ Tab changed """
        if page_num == 3:
            self.selected_files.get_selection().set_mode(gtk.SELECTION_SINGLE)
        else:
            self.selected_files.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
            

    def on_copy_activate(self, widget):
        """ Copy to clipboard """
        w = self.main_window.get_focus()
        if isinstance(w, gtk.Entry):
            w.emit('copy-clipboard')
        
        
    def on_paste_activate(self, widget):
        """ Paste from clipboard """
        w = self.main_window.get_focus()
        if isinstance(w, gtk.Entry):
            w.emit('paste-clipboard')
        
        
    def on_cut_activate(self, widget):
        """ Cut to clipboard """
        w = self.main_window.get_focus()
        if isinstance(w, gtk.Entry):
            w.emit('cut-clipboard')
        
        
    def on_clear_activate(self, widget):
        """ Clear text widget """
        w = self.main_window.get_focus()
        if isinstance(w, gtk.Entry):
            w.set_text('')
        
        
    def on_select_all_activate(self, widget):
        """ Select every row on selected-files treeview """
        self.selected_files.get_selection().select_all()
        
        
    def on_select_nothing_activate(self, widget):
        """ Select nothing on selected-files treeview """
        self.selected_files.get_selection().unselect_all()


    def on_main_quit(self, *args):
    	""" Bye bye! But first, save preferences """
        self.populate_stop()
        if HAS_GCONF: self.preferences_save()
        gtk.main_quit()


#---------------------------------------------------------------------------------------
# Directory functions

    def dir_reload_current(self):
        """ An easy way to call dir_selected """
        self.dir_selected(None, self.current_dir)
        

    def dir_selected(self, obj, dir):
    	""" The user has clicked on a directory on the left pane, so we need to load
    	the files inside that dir on the right pane. """
        
        self.current_dir = dir
        self.populate_stop()
        
        self.stop_button.show()
        self.rename_button.set_sensitive(False)
        self.file_selected_model.clear()
        
        self.populate_selected_files(dir)
        self.selected_files.columns_autosize()
        self.statusbar.push(self.statusbar_context, _("Reading contents of dir %s") % dir)
        
        
    def populate_stop(self):
        """ Stop populating the TreeView """
        
        renamerfilefuncs.set_stop(True)
        
        if self.listing_thread != None:
            while self.listing_thread.isAlive():
                self.listing_thread.join()
        
        self.stop_button.hide()
        for i in self.populate_id:
            removed = gobject.source_remove(i)
            self.populate_id.remove(i)
            
        self.selected_files.set_model(self.file_selected_model)
        self.progressbar.set_fraction(0)
        self.statusbar.push(self.statusbar_context, _("Directory: %s - Files: %s") % (self.current_dir, self.count))
        
        
    def populate_get_listing(self, dir, pattern, recursive):
        """ Get the file listing using the utilities on renamerfilefuncs """

        # Add files from the current directory (and subdirs if needed)
        if recursive:
            self.listing = renamerfilefuncs.get_file_listing_recursive(dir, pattern)
        else:
            self.listing = renamerfilefuncs.get_file_listing(dir, pattern)

        gobject.idle_add(self.populate_get_listing_end)
        

    def populate_get_listing_end(self):
        """ The listing thread stuff is over, so now add things to the view """
        
        if renamerfilefuncs.get_stop():
            self.populate_stop()
        else:
            populate = self.populate_add_to_view(self.listing)
            self.populate_id.append(gobject.idle_add(populate.next))


    def populate_selected_files(self, dir):
    	""" Get the file listing using the utilities on renamerfilefuncs.
    	Then add it to the model while updating the gui """
    
        pattern = self.file_pattern.get_text()
        recursive = self.add_recursive.get_active()
        
        renamerfilefuncs.set_stop(False)
        
        self.listing_thread = threading.Thread(target=lambda:self.populate_get_listing(dir, pattern, recursive))
        self.listing_thread.start()
        
        return
    
    
    def populate_add_to_view(self, listing):
        """ Add files to the treeview """
        
        # Add items to treeview
        for elem in listing:
            iter = self.file_selected_model.insert_before(None, None)
            
            self.selected_files.set_model(None)
            self.file_selected_model.set_value(iter, 0, elem[0])
            self.file_selected_model.set_value(iter, 1, elem[1])
            
            self.progressbar.pulse()
            self.statusbar.push(self.statusbar_context, _("Adding file %s") % elem[1])
            self.count += 1
            yield True
    
        self.selected_files.set_model(self.file_selected_model)
        self.progressbar.set_fraction(0)
        self.statusbar.push(self.statusbar_context, _("Directory: %s - Files: %s") % (self.current_dir, self.count))
        self.stop_button.hide()
        self.count = 0
        yield False


#---------------------------------------------------------------------------------------
# Dialog methods

    def display_error_dialog(self, text):
    	""" Yeps, it shows a error dialog """
        dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, text)
        dialog.run()
        dialog.destroy()


    def about_info(self,event,data=None):
        """ Display the About dialog """

        about = gtk.AboutDialog()
        about.set_name(pyrenamerglob.name_long)
        about.set_version(pyrenamerglob.version)
        about.set_authors(pyrenamerglob.authors)
        #about.set_artists(pyrenamerglob.artists)
        #about.set_translator_credits(_('translator-credits'))
        about.set_logo(gtk.gdk.pixbuf_new_from_file(pyrenamerglob.icon))
        about.set_license(pyrenamerglob.license)
        about.set_wrap_license(True)
        about.set_comments(pyrenamerglob.description)
        about.set_copyright(pyrenamerglob.copyright)

        def openHomePage(widget,url,url2):
            import webbrowser
            webbrowser.open_new(url)
	gtk.about_dialog_set_url_hook(openHomePage,pyrenamerglob.website)
        about.set_website(pyrenamerglob.website)
        
        about.run()
        about.destroy()


#---------------------------------------------------------------------------------------
# Preferences handling (Using Gconf)
        
    def preferences_save(self):
        """ Width and height are saved on the configure_event callback for main_window """      
        client = gconf.client_get_default()
        #client.set_string(self.gconf_key_dir, self.current_dir)
        client.set_int(self.gconf_pane_position, self.main_hpaned.get_position())
        client.set_bool(self.gconf_window_maximized, self.window_maximized)
        client.set_int(self.gconf_window_width, self.window_width)
        client.set_int(self.gconf_window_height, self.window_height)
        client.set_int(self.gconf_window_posx, self.window_posx)
        client.set_int(self.gconf_window_posy, self.window_posy)

        
    def preferences_read(self):
    	""" The name says it all... """
        client = gconf.client_get_default()
        
        #current_dir = client.get_string(self.gconf_key_dir)
        #if current_dir != None: self.current_dir = current_dir
        
        pane_position = client.get_int(self.gconf_pane_position)
        if pane_position != None: self.main_hpaned.set_position(pane_position)
            
        maximized = client.get_bool(self.gconf_window_maximized)
        if maximized != None and maximized == True: self.main_window.maximize()
        
        width = client.get_int(self.gconf_window_width)
        height = client.get_int(self.gconf_window_height)
        if width != None and height != None: self.main_window.resize(width, height)
        
        posx = client.get_int(self.gconf_window_posx)
        posy = client.get_int(self.gconf_window_posy)
        if posx != None and posy != None: self.main_window.move(posx, posy)

