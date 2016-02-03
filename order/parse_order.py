import mechanize
import re
from pyquery import PyQuery as pq

def monkeypatch_mechanize():
    """Work-around for a mechanize 0.2.5 bug. See: https://github.com/jjlee/mechanize/pull/58"""
    if mechanize.__version__ < (0, 2, 6):
        from mechanize._form import SubmitControl, ScalarControl

        def __init__(self, type, name, attrs, index=None):
            ScalarControl.__init__(self, type, name, attrs, index)
            # IE5 defaults SUBMIT value to "Submit Query"; Firebird 0.6 leaves it
            # blank, Konqueror 3.1 defaults to "Submit".  HTML spec. doesn't seem
            # to define this.
            if self.value is None:
                if self.disabled:
                    self.disabled = False
                    self.value = ""
                    self.disabled = True
                else:
                    self.value = ""
            self.readonly = True

        SubmitControl.__init__ = __init__

class CheckOrders(object):
    def check_one_order(self, order_number, email):
        self.browser.open("https://catalog.usmint.gov/track-order")
        self.browser.select_form(nr=2)
        self.browser.form['dwfrm_ordertrack_orderNumber'] = order_number
        self.browser.form['dwfrm_ordertrack_emailAddress'] = email
        response = self.browser.submit()
        html = response.get_data()
        pq_html = pq(html)
        status = pq_html('.order-status .value').text()
        tracking = ship_date = ''

        if status == 'SHIPPED':
            tracking = pq_html('.trackingnumber strong').text()
            ship_date = pq_html('.trackingnumber .value').eq(0).text()
            print tracking, ship_date

        return status, tracking, ship_date

    def check_shipping(self, tracking_numbers):
        self.browser.open("https://wwwapps.ups.com/WebTracking/track")
        self.browser.select_form(name='trkbynum')
        self.browser.form['trackNums'] = '\n'.join(tracking_numbers)
        response = self.browser.submit()
        html = response.get_data()
        pq_html = pq(html)
        tracking_dictionary = {}
        for tracking_number in tracking_numbers:
            order = pq_html('#descText' + tracking_number).parents('.secLvl.secLvlPlain.detail').parent()
            if len(tracking_numbers) == 1:
                order = order.parent()
            status = order('.infoAnchor.btnIconR.hozAnchor').eq(0).text()
            if status == 'Delivered':
                deliver_date = order('dd').eq(0).text()
                result = re.search('\d{1,2}/\d{1,2}/\d{2,4}', deliver_date)
                if result:
                    deliver_date = result.group(0)
                else:
                    deliver_date = None
            else:
                deliver_date = None
            tracking_dictionary[tracking_number] = {
                'status': status,
                'deliver_date': deliver_date
            }
        # print tracking_dictionary
        return tracking_dictionary


    def __init__(self):
        monkeypatch_mechanize()
        browser = mechanize.Browser()
        browser.set_handle_equiv(True)
        browser.set_handle_redirect(True)
        browser.set_handle_referer(True)
        browser.set_handle_robots(False)
        browser.addheaders = [('user-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3')]
        self.browser = browser

    def __del__(self):
        self.browser.close()


if __name__ == "__main__":
    CheckOrders().check_shipping(['1ZA5983WA802644897', '1ZA5983WA802660913'])