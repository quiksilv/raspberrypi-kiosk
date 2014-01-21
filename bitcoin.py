import os, logging, wx, time, datetime, Queue, printer, textwrap
from threading import *
from Datasource import Datasource

q = Queue.Queue()
class Main(wx.Frame):
	def __init__(self, parent, title):
		super(Main, self).__init__(parent, title=title, size=(640, 350) )
		self.panel = wx.Panel(self)
		self.hbox_input = wx.BoxSizer(wx.HORIZONTAL)
		currentPrice = "NA"
		data_worker = DataWorker('get_price')
		data_in_queue = q.get()
		currentPrice = data_in_queue['price']
		self.hbox_input.Add(wx.StaticText(self.panel, wx.NewId(), "Current Price: " + currentPrice), wx.EXPAND )
		self.Show()

class DataWorker(Thread):
	def __init__(self, action):
		Thread.__init__(self)
		self.action = action
		self.start()
	def run(self):
		d = Datasource()
		result = d.get_price()
		q.put(result)
def main():
	app = wx.App()
	Main(None, "Square Potato")
	app.MainLoop()

if __name__ == '__main__':
	main()

