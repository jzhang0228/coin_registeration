from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import xlrd, xlwt
import time
import pdb

from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

#did not work....
def disableImages(self):
    ## get the Firefox profile object
    firefoxProfile = FirefoxProfile()
    ## Disable CSS
    #firefoxProfile.set_preference('permissions.default.stylesheet', 2)
    ## Disable images
    firefoxProfile.set_preference('permissions.default.image', 2)
    ## Disable Flash
    firefoxProfile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so',
                                  'false')
    ## Set the modified profile while creating the browser object 
    self.browserHandle = webdriver.Firefox(firefoxProfile)

#def should go before it is called...

def checkOrder(orderId, emailAddress):    
    
    #once the main page is accessed, directly get(url) will work. 
    driver.get("https://catalog.usmint.gov/track-order")
    

    #elem = driver.find_element_by_link_text("Track Order")
    #elem.send_keys(Keys.RETURN) #directed to track_order page
    
    #fill in order# and last name, then submit
    elem = driver.find_element_by_name("dwfrm_ordertrack_orderNumber")
    elem.send_keys(orderId)
    elem = driver.find_element_by_name("dwfrm_ordertrack_emailAddress")
    elem.send_keys(emailAddress)
    elem.send_keys(Keys.RETURN) #directed to the track_result page
    
    print orderId
    #global tracking, shipDate
    #read the track order result
    try:#if the order can be found
        elem = driver.find_element_by_css_selector('.order-status .value')
        orderStatus  = elem.get_attribute("innerHTML")      
                
        if "SHIPPED" in orderStatus:            
            #tracking = driver.find_element_by_css_selector('.trackingnumber .value strong a').get_attribute("innerHTML")
            #tracking = driver.find_element_by_css_selector('.trackingnumber strong').get_attribute("innerHTML")
            tracking = driver.find_element_by_css_selector('.trackingnumber strong').text
            shipDate = driver.find_element_by_css_selector('.trackingnumber span:nth-child(2)').get_attribute("innerHTML")
        
    except:#if provided last name and order number do not match 
        orderStatus = "NOT FOUND"      
    
    print "orderStatus =",orderStatus, "tracking =",tracking, "shipDate=", shipDate
        
    #driver.switchTo().alert().dismiss()
    driver.implicitly_wait(5)
    #if EC.alert_is_present:
    #    driver.switch_to_alert().dismiss()
    return orderStatus, tracking, shipDate


driver = webdriver.Firefox()
#disableImages(driver)
driver.get("http://catalog.usmint.gov/on/demandware.store/Sites-USM-Site/default/CustomerService-Show?_ga=1.85706009.1605953677.1414357435") #have to begin from the main page
assert "Mint" in driver.title

#evertime change this file to the last updated one. xlrd can read xlsx, while xlwt can only write xls.
file_location = "/Users/jinzhang/Downloads/12_8_2015order.xls"

#function of xlrd
oldBook = xlrd.open_workbook(file_location)
oldSheet = oldBook.sheet_by_index(0)

#function of xlwt
newBook = xlwt.Workbook()
#pay attention to cell_overwrite_ok=True
newSheet = newBook.add_sheet('PM8orderStatus'+ time.strftime("%m%d%Y %H_%M_%S"), cell_overwrite_ok=True)

#copy the ENTIRE old file to new file
for col in range(oldSheet.ncols):
    for row in range(oldSheet.nrows):     
        newSheet.write(row, col, oldSheet.cell_value(row, col))

#add the most updated status column        
newSheet.write(0,oldSheet.ncols, 'status'+ time.strftime("%m%d %H:%M"))
    
#for row in range(1,24):#a shorter range for test.
for row in range(1, oldSheet.nrows): #the real range of form
    
    orderMultiple = oldSheet.cell_value(row, 12)
    trackingMultiple = ''
    shipDateMultiple = ''
    orderStatusMultiple = ''
    shippedCount = processingCount = onHoldCount = notFoundCount = cancelledCount = 0

    
    #print "orderMultiple=", orderMultiple
    
    for order in orderMultiple.split('\n'):
        orderId = order[0:11]
        emailAddress = order[11:].strip()
        #print orderId, emailAddress
  
        #emailAddress = oldSheet.cell_value(row, 11)
        tracking = shipDate = orderStatus = ''        
        
        try:
            orderStatus, tracking, shipDate = checkOrder(orderId, emailAddress)
        except:
        #    driver.switch_to_alert().dismiss()
        #    orderStatus, tracking, shipDate = checkOrder(orderId, emailAddress)
        #except:
        #    #close and reopen the page
        #    driver.close()            
        #    driver = webdriver.Firefox()
        #    #disableImages(driver)
        #    driver.get("http://catalog.usmint.gov/on/demandware.store/Sites-USM-Site/default/CustomerService-Show?_ga=1.85706009.1605953677.1414357435") #have to begin from the main page
        #    assert "Mint" in driver.title
        #    orderStatus = "EXCEPTION"
        #else:
            break
                
            
        trackingMultiple += (tracking+'\n')
        shipDateMultiple += (shipDate+'\n')
        orderStatusMultiple += (orderStatus+'\n')
        print "orderStatus =",orderStatus, "tracking =",tracking, "shipDate=", shipDate 

    newSheet.write(row, 20, trackingMultiple)
    newSheet.write(row, 21, shipDateMultiple)
    newSheet.write(row, 19, orderStatusMultiple)
    print "trackingMultiple=", trackingMultiple
    print "shipDateMultiple=", shipDateMultiple
    print "orderStatusMultiple=", orderStatusMultiple
    
        #print orderId, orderStatus, tracking, shipDate
        
        ##only orders of certain status need updating
        #if oldSheet.cell_value(row, oldSheet.ncols-1) == 'on hold' or oldSheet.cell_value(row, oldSheet.ncols-1) == 'in process':
        #    orderStatus, tracking, shipDate = checkOrder(orderId, emailAddress, tracking, shipDate)
        #    newSheet.write(row, 13, tracking)
        #    newSheet.write(row, 14, shipDate)
        #    print orderId, orderStatus, tracking, shipDate
        #    
        #else:#otherwise just use the old status
        #    orderStatus = oldSheet.cell_value(row, oldSheet.ncols-1)
        #    
        #newSheet.write(row, oldSheet.ncols, orderStatus)
        #
        ##record when the status changed
        #if orderStatus != oldSheet.cell_value(row, oldSheet.ncols-1):
        #    newSheet.write(row, 17, time.strftime("%m%d %H:%M"))
        
newBook.save('C:/Python27/GLY/PM8/PM8MultipleOrderStatus'+ time.strftime("%m%d%Y %H_%M_%S")+'.xls')  


driver.close()