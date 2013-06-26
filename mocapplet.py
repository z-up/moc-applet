#!/usr/bin/env python
import os, re, sys, subprocess

import gtk
import appindicator

class MocpApplet:
    def __init__(self):

        iconPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "headphones_32.png")
        self.polling_frequency = 5
        self.ind = appindicator.Indicator(
            "MyApp",
            iconPath,
            appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)

        if self.start_server():
            self.menu_setup()
            self.ind.set_menu(self.menu)
            self.check_server_status()
        else:
            self.state = 'ERROR'
            self.menu_setup2()
            self.ind.set_menu(self.menu)


    def menu_setup(self):
        self.menu = gtk.Menu()

        self.play_item = gtk.ImageMenuItem(gtk.STOCK_MEDIA_PLAY)
        self.play_item.connect("activate", self.play)
        self.play_item.show()
        self.menu.append(self.play_item)

        self.prev_item = gtk.ImageMenuItem(gtk.STOCK_MEDIA_PREVIOUS)
        self.prev_item.connect("activate", self.prev)
        self.prev_item.show()
        self.menu.append(self.prev_item)

        self.next_item = gtk.ImageMenuItem(gtk.STOCK_MEDIA_NEXT)
        self.next_item.connect("activate", self.next)
        self.next_item.show()
        self.menu.append(self.next_item)

        self.stop_item = gtk.ImageMenuItem(gtk.STOCK_MEDIA_STOP)
        self.stop_item.connect("activate", self.stop)
        self.stop_item.show()
        self.menu.append(self.stop_item)

        self.quit_item = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)



    def menu_setup2(self):
        self.menu = gtk.Menu()

        self.msg_item = gtk.MenuItem('Failed to start server')
        self.msg_item.show()
        self.menu.append(self.msg_item)

        self.quit_item = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)


    def main(self):
        if self.state != 'ERROR':
            gtk.timeout_add(self.polling_frequency * 1000, self.check_server_status)
        gtk.main()


    def send_command(self, command):
        process = subprocess.Popen(
            "mocp --%s" % command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        (stdoutdata, stderrdata) = process.communicate()
        self.check_server_status()


    def play(self, widget):
        if self.state == 'STOP':
            self.send_command('play')
        else:
            self.send_command('toggle-pause')


    def prev(self, widget):
        self.send_command('previous')


    def next(self, widget):
        self.send_command('next')

    def stop(self, widget):
        self.send_command('stop')



    def quit(self, widget):
        sys.exit(0)


    def check_server_status(self):
        process = subprocess.Popen(
            "mocp --info",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        (stdoutdata, stderrdata) = process.communicate()
        if process.returncode != 0:
            if self.start_server(): # restart server in case it was stopped from GUI
                return self.check_server_status()
            else:
                return False

        state = re.findall(r'State: ([A-Z]+)\n', stdoutdata, re.MULTILINE)[0]

        self.state = state
        if state == 'PLAY':
            self.play_item.get_image().set_from_stock(gtk.STOCK_MEDIA_PAUSE, gtk.ICON_SIZE_MENU)
            self.play_item.set_label('Pause')
            self.stop_item.set_sensitive(True)
            self.prev_item.set_sensitive(True)
            self.next_item.set_sensitive(True)
        elif state == 'PAUSE':
            self.play_item.get_image().set_from_stock(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_MENU)
            self.play_item.set_label('Resume')
            self.stop_item.set_sensitive(True)
            self.prev_item.set_sensitive(True)
            self.next_item.set_sensitive(True)
        elif state == 'STOP':
            self.play_item.get_image().set_from_stock(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_MENU)
            self.play_item.set_label('Play')
            self.stop_item.set_sensitive(False)
            self.prev_item.set_sensitive(False)
            self.next_item.set_sensitive(False)

        return True


    def start_server(self):
        process = subprocess.Popen(
            "mocp --server",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        (stdoutdata, stderrdata) = process.communicate()
        if process.returncode == 0 or\
                re.findall('FATAL_ERROR: Server is already running!', stdoutdata):
            return True
        else:
            return False


if __name__ == "__main__":
    indicator = MocpApplet()
    indicator.main()


