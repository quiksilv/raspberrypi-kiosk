import os
import logging
from i18n import i18n
import wx
import time
import datetime
import Queue
from threading import *
import thread
import printer, textwrap
from billacceptor import BillAcceptor
from TShop import TShop

q = Queue.Queue()
ID_ABORT = wx.NewId()
ID_OK = wx.NewId()
ID_ZERO = wx.NewId()
ID_ONE = wx.NewId()
ID_TWO = wx.NewId()
ID_THREE = wx.NewId()
ID_FOUR = wx.NewId()
ID_FIVE = wx.NewId()
ID_SIX = wx.NewId()
ID_SEVEN = wx.NewId()
ID_EIGHT = wx.NewId()
ID_NINE = wx.NewId()
ID_CLEAR = wx.NewId()
ID_BACK = wx.NewId()
ID_RECIPIENT_NUMBER = wx.NewId()
ID_WELCOME_TEXT = wx.NewId()
# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()


class ResultEvent(wx.PyEvent):
	"""Simple event to carry arbitrary result data."""
	def __init__(self, data):
		"""Init Result Event."""
		wx.PyEvent.__init__(self)
		self.SetEventType(EVT_RESULT_ID)
		self.data = data
class TShopWorker(Thread):
	def __init__(self, msisdn, selected_product):
		Thread.__init__(self)
		self.msisdn = msisdn
		self.selected_product = selected_product
		self.start()
	def run(self):
		t = TShop()
		result = t.topup('60168734755', self.msisdn, self.selected_product)
		if(result):
			q.put(result)
		else:
			result['error_txt'] = _('Local connection error')
			result['error_code'] = 'l0'
			q.put(result)
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
class Main(wx.Frame):
	def __init__(self, parent, title):
		super(Main, self).__init__(parent, title=title, size=(640, 350) )
		#super(Main, self).__init__(parent, title=title, size=wx.DisplaySize(), style=wx.NO_BORDER | wx.CAPTION )
		self.absolute_path = os.path.dirname(os.path.abspath(__file__))
		logging.basicConfig(filename = self.absolute_path + "/logs/usage" + time.strftime("%d%m%Y", time.localtime(time.time() ) )+'.log',level=logging.DEBUG)

		self.welcome_text = "Welcome"

		self.ln = i18n()
		self.ln.install()

		self.InitUI()
		self.Show()
	def ChangeLanguage(self, event, locale):
		self.ln.set_language(locale)
		self.ln.install()
		self.UpdateText()
	def UpdateText(self):
		#changes the text in buttons
		for widgets in self.pnl.GetChildren():
			if widgets.GetId() == ID_BACK:
				widgets.SetLabel(_('Back') )
			if widgets.GetId() == ID_CLEAR:
				widgets.SetLabel(_('Clear') )
			if widgets.GetId() == ID_RECIPIENT_NUMBER:
				widgets.SetLabel(_('Recipient Number') )
			if widgets.GetId() == ID_WELCOME_TEXT:
				widgets.SetLabel(_(self.welcome_text) )
			if widgets.GetId() == ID_OK:
				widgets.SetLabel(_('Ok') )
	def AsciiToUnicode(self, ascii_text):
		decoded = ascii_text.decode('utf-8')
		unicode(decoded)
		return decoded
	def InitUI(self):   
		self.pnl = wx.Panel(self)
#		self.EVT_RESULT_ID1 = self.GetNewId()
#		self.EVT_RESULT_ID2 = self.GetNewId()

		self.Connect(-1, -1, EVT_RESULT_ID, self.OnResult)
		self.worker = None
		
		font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
		font.SetPointSize(12)
		self.pnl.SetFont(font)

		self.displayGUI()

	def displayGUI(self):

		self.vbox = wx.BoxSizer(wx.VERTICAL)

		#localization		
		localization= wx.BoxSizer(wx.HORIZONTAL)
		chinese = wx.Button(self.pnl, label=_('Chinese') )
		bengali = wx.Button(self.pnl, label=_('Bengali') )
		tagalog = wx.Button(self.pnl, label=_('Tagalog') )
		indonesian = wx.Button(self.pnl, label=_('Indonesian') )
		english = wx.Button(self.pnl, label=_('English') )
		chinese.Bind(wx.EVT_BUTTON, lambda event: self.ChangeLanguage(event, 'zh_CN') )
		bengali.Bind(wx.EVT_BUTTON, lambda event: self.ChangeLanguage(event, 'bn_BD') )
		tagalog.Bind(wx.EVT_BUTTON, lambda event: self.ChangeLanguage(event, 'tl_PH') )
		indonesian.Bind(wx.EVT_BUTTON, lambda event: self.ChangeLanguage(event, 'id_ID') )
		english.Bind(wx.EVT_BUTTON, lambda event: self.ChangeLanguage(event, 'en_US') )
		localization.Add(chinese)
		localization.Add(bengali)
		localization.Add(tagalog)
		localization.Add(indonesian)
		localization.Add(english)
		self.vbox.Add(localization, flag = wx.ALIGN_RIGHT | wx.RIGHT | wx.TOP, border = 10)

		self.hbox_input = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox_input.Add(wx.Button(self.pnl, id=ID_BACK, label=_('Back') ) )
		self.pnl.Bind(wx.EVT_BUTTON, self.ClearProductBox, id=ID_BACK)
		self.hbox_input.Add(wx.StaticText(self.pnl, id=ID_RECIPIENT_NUMBER, label=_('Recipient Number') ), wx.EXPAND )
		self.msisdn_info = wx.TextCtrl(self.pnl, value="628123456770")
		mbtn = wx.Button(self.pnl, id=ID_OK, label=_('Ok') )
		mbtn.Bind(wx.EVT_BUTTON, self.OnOk)
		self.defaultStatusBar = self.CreateStatusBar()
		self.hbox_input.Add(self.msisdn_info, wx.EXPAND)
		self.hbox_input.Add(mbtn)
		self.vbox.Add(self.hbox_input, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 10)

		gs = wx.GridSizer(4, 3, 1, 1)
		gs.AddMany( [
		    (wx.Button(self.pnl, id=ID_SEVEN, label='7'), 0, wx.EXPAND |  wx.LEFT, 10),
		    (wx.Button(self.pnl, id=ID_EIGHT, label='8'), 0, wx.EXPAND),
		    (wx.Button(self.pnl, id=ID_NINE, label='9'), 0, wx.EXPAND),
		    (wx.Button(self.pnl, id=ID_FOUR, label='4'), 0, wx.EXPAND | wx.LEFT, 10),
		    (wx.Button(self.pnl, id=ID_FIVE, label='5'), 0, wx.EXPAND),
		    (wx.Button(self.pnl, id=ID_SIX, label='6'), 0, wx.EXPAND),
		    (wx.Button(self.pnl, id=ID_ONE, label='1'), 0, wx.EXPAND | wx.LEFT, 10),
		    (wx.Button(self.pnl, id=ID_TWO, label='2'), 0, wx.EXPAND),
		    (wx.Button(self.pnl, id=ID_THREE, label='3'), 0, wx.EXPAND),
		    (wx.Button(self.pnl, id=ID_ZERO, label='0'), 0, wx.EXPAND | wx.LEFT, 10),
		    (wx.Button(self.pnl, id=ID_CLEAR, label=_('Clear') ), 0, wx.EXPAND)
		] )
		self.pnl.Bind(wx.EVT_BUTTON, self.KeyClicked, id=ID_ZERO)
		self.pnl.Bind(wx.EVT_BUTTON, self.KeyClicked, id=ID_ONE)
		self.pnl.Bind(wx.EVT_BUTTON, self.KeyClicked, id=ID_TWO)
		self.pnl.Bind(wx.EVT_BUTTON, self.KeyClicked, id=ID_THREE)
		self.pnl.Bind(wx.EVT_BUTTON, self.KeyClicked, id=ID_FOUR)
		self.pnl.Bind(wx.EVT_BUTTON, self.KeyClicked, id=ID_FIVE)
		self.pnl.Bind(wx.EVT_BUTTON, self.KeyClicked, id=ID_SIX)
		self.pnl.Bind(wx.EVT_BUTTON, self.KeyClicked, id=ID_SEVEN)
		self.pnl.Bind(wx.EVT_BUTTON, self.KeyClicked, id=ID_EIGHT)
		self.pnl.Bind(wx.EVT_BUTTON, self.KeyClicked, id=ID_NINE)
		self.pnl.Bind(wx.EVT_BUTTON, self.KeyClicked, id=ID_CLEAR)

		self.vbox_products = wx.BoxSizer(wx.VERTICAL)
		self.vbox_products.Add(wx.StaticText(self.pnl, id=ID_WELCOME_TEXT, label=_(self.welcome_text) ), flag = wx.EXPAND)

		self.hbox_content = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox_content.Add(gs, proportion=1, flag=wx.EXPAND) #the keypad
		self.hbox_content.Add(self.vbox_products, proportion=1, flag=wx.EXPAND) #the product list
		self.vbox.Add(self.hbox_content, proportion=1)

		advertisement = wx.BoxSizer(wx.HORIZONTAL)
		advertisement.Add(wx.StaticBitmap(self.pnl, -1, wx.Image(self.absolute_path + "/images/deploy_SquarePotato1_web.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap() ) )
		self.vbox.Add(advertisement, flag=wx.EXPAND | wx.ALL, border = 20)
		self.pnl.SetSizer(self.vbox)
	def ClearProductBox(self, event):
		self.vbox_products.DeleteWindows()
	def KeyClicked(self, event):
		self.log("KeyClicked event")
		original = self.msisdn_info.GetValue();
		if(event.GetId() == ID_ZERO):
			self.msisdn_info.SetValue(original + "0")
		elif(event.GetId() == ID_ONE):
		     self.msisdn_info.SetValue(original + "1")
		elif(event.GetId() == ID_TWO):
		     self.msisdn_info.SetValue(original + "2")
		elif(event.GetId() == ID_THREE):
		     self.msisdn_info.SetValue(original + "3")
		elif(event.GetId() == ID_FOUR):
		     self.msisdn_info.SetValue(original + "4")
		elif(event.GetId() == ID_FIVE):
			self.msisdn_info.SetValue(original + "5")
		elif(event.GetId() == ID_SIX):
			self.msisdn_info.SetValue(original + "6")
		elif(event.GetId() == ID_SEVEN):
			self.msisdn_info.SetValue(original + "7")
		elif(event.GetId() == ID_EIGHT):
			self.msisdn_info.SetValue(original + "8")
		elif(event.GetId() == ID_NINE):
			self.msisdn_info.SetValue(original + "9")
		elif(event.GetId() == ID_CLEAR):
			self.msisdn_info.SetValue("")
	def GetNewId(self):
		return wx.NewId()
	def OnOk(self, event):
		self.log(self.msisdn_info.GetValue() + " OnOk event")
		self.vbox_products.DeleteWindows()
		#dialog box to notify start of TShop query
		self.defaultStatusBar.SetStatusText(_('Please wait, querying server...') )
		wx.CallAfter(self._generateButtons)
		t = TShop()
		result = t.msisdn_info(self.msisdn_info.GetValue() )
		if not result:
			result['error_txt'] = _('Local connection error')
			result['error_code'] = 'l0'
		self.msisdn_info_query_result = result
			
		self.defaultStatusBar.SetStatusText('Ok')
	def OnAbort(self, event):
		self.log("Abort event")
		if self.worker:
			self.worker.abort()
			self.vbox_products.DeleteWindows()
			self.defaultStatusBar.SetStatusText(_('Aborted') )
			self.worker = None
	def OnProductSelect(self, event):
		self.log("OnProductSelect event")
		for sizerItem in self.vbox_products.GetChildren():
			widget = sizerItem.GetWindow()
			if(widget == None):
				continue
			if(widget.GetId() != ID_ABORT ):
				widget.Disable()

		eventObject = event.GetEventObject().GetLabel().split("\t")
		print eventObject
		self.selectedProduct = eventObject[0].split(" ")[1]
		self.selectedProductValue = (eventObject[1].split("\n")[0]).split(" ")[1]
		self.selectedServiceFee = eventObject[1].split(" ")[6]
		self.defaultStatusBar.SetStatusText(_('Please insert exact amount...') )
		self.worker = Acceptor(self, {
			'msisdn' : self.msisdn_info.GetValue(),
			'selected_product' : self.selectedProduct,
			'selected_product_value' : self.selectedProductValue,
			'selected_service_fee' : self.selectedServiceFee
		})
		#self.result = q.get()
		#self._updateStatus()
	def _updateStatus(self):
		self.log("_updateStatus event")
		self.vbox_products.DeleteWindows()
		if(self.result is not None):
			if os.environ['DEV_HOSTNAME'] == "squarepotato-1":
				print self.result
			else:
				#activate physical printer if not working on laptop
				self.printReceipt(self.result)

			self.defaultStatusBar.SetStatusText(_('Done') )

			self.vbox_products.Add(wx.StaticText(self.pnl, label=_(self.result['error_txt']) ), flag = wx.EXPAND) 
			#Very ugly error codes
			if(self.result['error_code'] != 'l0' and self.result['error_code'] != 'l1'):
				#for TShop errors. l0 and l1 are locally generated python request connection errors
				#
				#	self.result = {
				#		'error_code' : 'l0' #or 'l1'
				#		'error_txt' : 'Local connection error' #or 'Timeout'
				#	}
				#
				self.vbox_products.Add(wx.StaticText(self.pnl, label=self.result['return_timestamp']), flag = wx.EXPAND)
				self.vbox_products.Add(wx.StaticText(self.pnl, label=self.AsciiToUnicode(_("Operator: ") ) + self.result['operator']), flag = wx.EXPAND)
				self.vbox_products.Add(wx.StaticText(self.pnl, label=self.AsciiToUnicode(_("Recipient Number: ") ) + self.result['destination_msisdn']), flag = wx.EXPAND)
				self.vbox_products.Add(wx.StaticText(self.pnl, label=self.AsciiToUnicode(_("Product Sent: ") ) + self.result['destination_currency'] + " " + self.result['actual_product_sent']), flag = wx.EXPAND)
				self.vbox_products.Add(wx.StaticText(self.pnl, label=self.AsciiToUnicode(_("You paid: ") ) + self.result['originating_currency'] + " " + self.result['retail_price'] + " with serv. fee: " + self.result['originating_currency'] + " " + self.result['service_fee'] ), flag = wx.EXPAND)
			size = self.GetSize()
			self.pnl.SetSize((size.GetWidth(), size.GetHeight() ) )
			self.pnl.Layout()
		
	def printReceipt(self, result):
		self.log("printReceipt event")
		p = printer.ThermalPrinter(serialport="/dev/ttyAMA0") #GPIO pins
		p.print_text(textwrap.fill("SquarePotato Prototype 1 - START") )
		p.linefeed()
		p.print_text(textwrap.fill("Status:" + result['error_txt']) )
		p.linefeed()
		p.print_text(textwrap.fill("Time: " + result['return_timestamp']) )
		p.linefeed()
		p.print_text(textwrap.fill("Operator: " + result['operator']) )
		p.linefeed()
		p.print_text(textwrap.fill("Sent: " + result['destination_currency'] + " " + result['actual_product_sent']) )
		p.linefeed()
		p.print_text(textwrap.fill("SquarePotato Prototype 1 - END") )
		p.linefeed()
		p.linefeed()
		p.linefeed()
		p.linefeed()
	def _generateButtons(self):
		self.log("generateButtons event")
		self.vbox_products.DeleteWindows()
#		for child in self.pnl.GetChildren():
#			if(isinstance(child, wx.StaticText) or isinstance(child, wx.Button) ): 
#				if(child.GetLabel() != "Check" ):
#					child.Destroy()
		y = 0
		msisdn_info = self.msisdn_info_query_result
		if (msisdn_info['error_code'] != "0"):
			error = wx.StaticText(self.pnl, label=msisdn_info['error_txt'])
			error.SetForegroundColour(wx.RED)
			self.vbox_products.Add(error, flag = wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)
			wx.MessageBox(msisdn_info['error_txt'], 'Alert', wx.OK | wx.ICON_EXCLAMATION)
		else:
			operator_box = wx.BoxSizer(wx.HORIZONTAL)
			operator_box.Add(wx.StaticBitmap(self.pnl, -1, wx.Image(self.absolute_path + "/images/logo-" + msisdn_info['operatorid']+'-1.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap() ) );
			operator_box.Add(wx.StaticText(self.pnl, label=msisdn_info['operator']), flag = wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)
			self.vbox_products.Add(operator_box, flag=wx.EXPAND | wx.LEFT, border=10)
			for p in range(len(msisdn_info['product_list']) ):
				pbtn = wx.Button(self.pnl, wx.NewId(), label=msisdn_info['destination_currency'] + " " + msisdn_info['product_list'][p] + "\tSGD " + msisdn_info['retail_price_list'][p] + "\n with serv. fee: SGD " + msisdn_info['service_fee_list'][p])
				pbtn.Bind(wx.EVT_BUTTON, self.OnProductSelect)
				self.vbox_products.Add(pbtn, flag=wx.EXPAND | wx.LEFT, border=10)
				y += 1
			#Abort Button
			self.vbox_products.Add(wx.Button(self.pnl, ID_ABORT, label=_('Abort') ), flag=wx.EXPAND | wx.LEFT, border=10 )
			self.pnl.Bind(wx.EVT_BUTTON, self.OnAbort, id=ID_ABORT)


		size = self.GetSize()
		self.pnl.SetSize((size.GetWidth(), size.GetHeight() ) )
		self.pnl.Layout()
	def OnResult(self, event):
		"""Show Result status."""
		self.log("OnResult event")
		if event.data is None:
			# Thread aborted (using our convention of None return)
			#self.OnAbort(event)
			#self.defaultStatusBar.SetStatusText("Aborted")
			print "event.data is None"
		else:
			# Process results here
			self.result = event.data
			if(isinstance(self.result, basestring) ):
				self.defaultStatusBar.SetStatusText(_(self.result) )
			else:
				#self.result contains the result list
				if(self.result['error_code'] != '0'):
					wx.MessageBox(self.result['error_txt'], 'Alert', wx.OK | wx.ICON_EXCLAMATION)
				self._updateStatus()
		# In either event, the worker is done
		self.worker = None
	def log(self, message):
		logging.info("[" + str(datetime.datetime.fromtimestamp(int(time.time() ) ) ) + "] " + message)
def main():
	ex = wx.App()
	Main(None, "Square Potato")
	ex.MainLoop()    


if __name__ == '__main__':
    main()
