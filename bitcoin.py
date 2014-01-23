import os, logging, wx, time, datetime, Queue, printer, textwrap
from wx import xrc
from threading import *
from Datasource import Datasource

q = Queue.Queue()
EVT_RESULT_ID = wx.NewId()
class BitcoinATM(wx.App):

	def OnInit(self):
		self.res = xrc.XmlResource('gui.xrc')
		self.init_frame()
		return True
	def init_frame(self):
		self.frame = self.res.LoadFrame(None, 'mainFrame')
		self.scanPanel = xrc.XRCCTRL(self.frame, 'scanPanel')
		self.insertPanel = xrc.XRCCTRL(self.frame, 'insertPanel')
		self.insertPanel.Hide()
		self.boughtPanel = xrc.XRCCTRL(self.frame, 'boughtPanel')
		self.boughtPanel.Hide()
		self.price_label = xrc.XRCCTRL(self.scanPanel, 'price_label')
		self.identity_textbox = xrc.XRCCTRL(self.scanPanel, 'identity')
		self.identity_textbox.SetFocus()
		self.frame.Bind(wx.EVT_BUTTON, self.OnScanned, id=xrc.XRCID('next') )
		self.frame.Bind(wx.EVT_BUTTON, self.OnBuy, id=xrc.XRCID('buy') )
		self.frame.Bind(wx.EVT_BUTTON, self.OnAgain, id=xrc.XRCID('again') )
		self.Connect(-1, -1, EVT_RESULT_ID, self.OnResult)
		data_worker = DataWorker(self)
		self.frame.Show()
	def OnScanned(self, event):
		self.scanPanel.Hide()
		self.insertPanel.Show()
	def OnBuy(self, event):
		self.insertPanel.Hide()
		self.boughtPanel.Show()
	def OnAgain(self, event):
		self.boughtPanel.Hide()
		self.scanPanel.Show()
	def OnResult(self, event):
		self.price_label.SetLabel(str(event.data['exchange_rate']) )

class ResultEvent(wx.PyEvent):
	"""Simple event to carry arbitrary result data."""
	def __init__(self, data):
		"""Init Result Event."""
		wx.PyEvent.__init__(self)
		self.SetEventType(EVT_RESULT_ID)
		self.data = data
class DataWorker(Thread):
	def __init__(self, main_window):
		Thread.__init__(self)
		self._main_window = main_window
		self.d = Datasource()
		self.start()
	def run(self):
		while True:
			result = self.d.test()
			wx.PostEvent(self._main_window, ResultEvent(result) )
			time.sleep(1)
class Acceptor(Thread):
	def __init__(self, main_window, input_data):
		Thread.__init__(self)
		self._abort = False
		self.b = BillAcceptor()
		self.start()
		self.input_data = input_data
		self._main_window = main_window
	def run(self):
		tshop_worker = None
		result = []
		stacking = None
		iterator = 0
		start_time = time.time()
		#get inserted amount
		while True:
			status = self.b.run(iterator, stacking)
			if status is not None:
				if(status['status'] == 'IDLE' and time.time() - start_time > 10): #reset GUI after 10 seconds
					wx.PostEvent(self._main_window, ResultEvent({
						'error_code' : 'l1',
						'error_txt' : _('Timeout')
					}) )
					return
				#not very good.  Exiting immediately after assigning False to stacking, no chance to send Return signal
				#to the bill acceptor
				if(stacking == False or status['total'] == float(self.input_data['selected_product_value']) + float(self.input_data['selected_service_fee']) ):
					wx.PostEvent(self._main_window, ResultEvent(result) )
					self.b.close()
					return
					#break
				if(self._abort):
					wx.PostEvent(self._main_window, ResultEvent(None) )
					self.b.close()
					return
				if(status['status'] == 'ESCROWED' and stacking is None):
					wx.PostEvent(self._main_window, ResultEvent(_('Please wait, sending request to server...') ) )
					if not tshop_worker:
						tshop_worker = TShopWorker(self.input_data['msisdn'], self.input_data['selected_product'])
					if not q.empty():
						result = q.get()
						if(str(result['error_code']) == '0'):
							stacking = True
						else:
							stacking = False
				iterator += 1
				time.sleep(1)
				status_text = self.AsciiToUnicode(_('Please insert {selected_product_value}. You have inserted {total}.').format(selected_product_value=float(self.input_data['selected_product_value']) + float(self.input_data['selected_service_fee']), total=str(status['total']) ) )
				
				wx.PostEvent(self._main_window, ResultEvent(status_text) )
#					'Please insert ' + self.input_data['selected_product_value'] + '. You have inserted RM' + str(status['total']) + ".")
	def abort(self):
		self._abort = True
	#duplicate method, Main class has one as well
	def AsciiToUnicode(self, ascii_text):
		decoded = ascii_text.decode('utf-8')
		unicode(decoded)
		return decoded
if __name__ == '__main__':
	app = BitcoinATM(False)
	app.MainLoop()
