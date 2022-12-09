from selenium import webdriver
from  selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

import time
import datetime
import json
import smtplib
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from secrets import get_secret_burst, get_secret_frontier, get_secret_piedmont, get_secret_INI, get_secret_TIND

chromeOptions = Options()

def sendEmail(destination, filename, errorScreenshot, MRN):
    print("Sending email to "+ str(destination))
    try:
        fromaddr = "iphproreports@outlook.com"
        toaddr = destination
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Upload for ECW failed for "+str(MRN)
        # body = "ECW upload failed for "+str(MRN)
        # msg.attach(MIMEText(body, 'plain'))
        html = """\
        <html>
        <head></head>
        <body>
        <p> ECW Upload failed for {MRN} </p>
        </body>
        </html>""".format(MRN=MRN)
        msg.attach(MIMEText(html, 'html'))

        # attach the report file
        attachment = open(str(filename), "rb")
        p = MIMEBase('application', 'octet-stream')
        p.set_payload((attachment).read())
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        msg.attach(p)

        # attach the screenshot file
        attachment = open(str(errorScreenshot), "rb")
        p = MIMEBase('application', 'octet-stream')
        p.set_payload((attachment).read())
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', "attachment; filename= %s" % errorScreenshot)
        msg.attach(p)
        
        s = smtplib.SMTP('smtp.outlook.com', 587)
        s.starttls()
        s.login(fromaddr, "Iph2020admin!")
        text = msg.as_string()
        s.sendmail(fromaddr, toaddr, text)
        s.quit()
        print("Email sent successfully")
        return "Email sent correctly"
    except Exception as e:
        print(e)
        return "Email Error: "+str(e)


def add_file_TIND(mrn, filename):
    login=get_secret_TIND()
    # try to login five times
    for i in range(5):
        try:
            #pull up the page
            print(F"SELENIUM {mrn}, {filename}")
            chromeOptions.add_argument('--ignore-certificate-errors')
            chromeOptions.add_argument('--allow-running-insecure-content')
            chromeOptions.headless = True
            browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chromeOptions)
            browser.set_window_size(1366, 768, browser.window_handles[0])
            browser.get("https://txtenaapp.ecwcloud.com/mobiledoc/jsp/webemr/login/newLogin.jsp")
            
            # add username
            username_box= browser.find_element(By.ID,'doctorID')
            username_box.send_keys(str(login['username']))
            username_box.send_keys(Keys.ENTER)
            print("SELENIUM Added username")

            # add password
            password_box=browser.find_element(By.ID,'passwordField')
            password_box.clear()
            password_box.send_keys(str(login['password']))
            password_box.send_keys(Keys.ENTER)
            print("SELENIUM Added Password")

            # wait in case there is a popup
            time.sleep(5)
            try: 
                print("SELENIUM finding the popup")
                time.sleep(5)
                popup=browser.find_element(By.XPATH, '/html/body/div[1]/div[5]/div/div/div[2]/div[4]/table/tbody/tr/td[1]/button')
                popup.click()
                break
            except Exception as e:
                print("SELENIUM Pop up interactiion was not successful: "+str(e))

        except Exception as e:
            print(f"SELENIUM Login was not successful: {e}")
            return e
        
    try:
        # search for the right user
        print("SELENIUM finding user")
        box=browser.find_element(By.ID,'jellybean-panelLink65')
        box.click()

        # select the dropdown
        time.sleep(2)
        dropdown=browser.find_element(By.XPATH, '//*[@id="patient-lookup-screen-detview"]/div/div[1]/div[1]/div/div/div/div[2]/div/div')
        dropdown.click()

        # select the right patient
        time.sleep(2)
        MRN_selection=browser.find_element(By.XPATH, '//*[@id="patient-lookup-screen-detview"]/div/div[1]/div[1]/div/div/div/div[2]/div/ul/li[5]/a/span')
        MRN_selection.click()
        search=browser.find_element(By.ID, 'searchText')
        search.send_keys(str(mrn))
        time.sleep(2)
        search.send_keys(Keys.ENTER)

        # fill in the notes
        time.sleep(5)
        notes_button=browser.find_element(By.ID, 'patient-hubBtn9')
        notes_button.click()
        time.sleep(3)
        existing_note_text = browser.find_element(By.ID, 'toppanelcontainer')
        existing_string = existing_note_text.get_attribute("patientobj")
        existing_dict = json.loads(existing_string)
        existing_text = existing_dict["sticky_notes"]
        print(f"SELENIUM Existing: {existing_text}")
        time.sleep(3)
        notes_tab=browser.find_element(By.XPATH, '/html/body/div[3]/div[4]/section/div/div/section/div[2]/div/div[1]/div/div[1]/div[1]/div/div[1]/div[2]/div/div/div[3]')
        notes_tab.click()
        time.sleep(3)

        text_area=browser.find_element(By.ID, 'stickyNotesContent')
        text_area.clear()
        text_area.send_keys(f"PRO Questionnaire Report Ready {datetime.date.today()}\n{existing_text}")
        time.sleep(2)

        save_btn = browser.find_element(By.ID, 'topPanelBtn2')
        save_btn.click()
        time.sleep(2)

        # select document and insert
        docs=browser.find_element(By.XPATH, '//*[@id="topPanelLink23"]/font')
        docs.click()

        time.sleep(5)
        search_2=browser.find_element(By.ID, 'patientdocsIpt1')
        search_2.send_keys('X-')

        time.sleep(3)
        xray=browser.find_element(By.XPATH, '//*[@id="patientdocsTreeUl1"]')
        xray.click()
        add_local=browser.find_element(By.ID, 'patientdocsBtn4')
        input_form=browser.find_element(By.XPATH, '//*[@id="fileUpload"]')
        time.sleep(2)
        print("SELENIUM About to add")
        add_local.click()
        #driver.execute_script("arguments[0].removeAttribute('style')", input_form)

        # send the path to the file ('/home/ec2-user/'+)
        input_form.send_keys("/home/ec2-user/EHR_Bots/"+str(filename))


        add_local.submit()
        #input_form.submit()
        time.sleep(3)
        browser.close()
        print ("SELENIUM File added successfully")
        print ("SELENIUM Driver Closed")
        # browser.save_screenshot("upload.png")
        #refresh=driver.find_element(By.ID, 'patientdocsBtn6')
        #refresh.click()
        os.remove(filename)
        browser.quit()
        return ("This bitch uploaded")
        
    except Exception as e:
        print("SELENIUM Errored: "+str(e))
        browser.save_screenshot("Errored_Screenshot.png")
        time.sleep(5)

        # sendEmail("nmathur@iph.ai", str(filename), "ErroredScreenshot.png", mrn)
        sendEmail("sgupta@iph.ai", str(filename), "Errored_Screenshot.png", mrn)
        sendEmail("nsabatini@iph.ai", str(filename), "Errored_Screenshot.png", mrn)

        
    
def add_file_frontier(mrn, filename):
    login=get_secret_frontier()
    try:
        print(f"SELENIUM {mrn}, {filename}")
        chromeOptions.add_argument('--ignore-certificate-errors')
        chromeOptions.add_argument('--allow-running-insecure-content')
        chromeOptions.headless = True
        browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chromeOptions)
        browser.set_window_size(1366, 768, browser.window_handles[0])
        
        browser.get("https://athenanet.athenahealth.com/1/77/login.esp")
        username=browser.find_element(By.ID, "USERNAME")
        username.send_keys(str(login['username']))
        password=browser.find_element(By.ID, "PASSWORD")
        password.send_keys(str(login['password']))
        login=browser.find_element(By.ID,"loginbutton")
        login.click()
        login=browser.find_element(By.ID,"loginbutton")
        login.click()
        print("SELENIUM Sign in is complete")
        mrn=str(mrn)
        print("SELENIUM Locating patient")
        time.sleep(4)
        browser.switch_to.frame("GlobalNav")
        search=browser.find_element(By.XPATH, '//*[@id="searchinput"]')
        search.send_keys(mrn)
        search.send_keys(Keys.RETURN)
        browser.switch_to.parent_frame()
        print("SELENIUM uploading PDF")
        #wait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it(driver.find_element(By.XPATH, '//*[@id="GlobalWrapper"]')))
        time.sleep(3)

        browser.switch_to.frame("GlobalWrapper")
        browser.switch_to.frame("frameContent")
        print("SELENIUM iframe switched to frame content")
        browser.switch_to.frame("frMain")
        print("SELENIUM iframe switched to frMain")

        
        
        recent_test=browser.find_element(By.XPATH, '//*[@id="page-body"]/div[3]/div[8]/div[2]/div/div/div[2]/div/div/div[2]/ul/li[2]/button')
        recent_test.click()

        menu_toggle=browser.find_element(By.XPATH, '//*[@id="page-body"]/div[3]/div[6]/div[2]/div[1]/div/div')
        menu_toggle.click()
        add_documents=browser.find_element(By.XPATH, '/html/body/div[6]/div/div/div/ul/li[5]/div[1]')
        add_documents.click()
        time.sleep(5)
        toggle_upload=browser.find_element(By.XPATH, '/html/body/div[7]/div/div/div[2]/ul/li[3]/div[1]')
        toggle_upload.click()

        time.sleep(3)
        select = Select(browser.find_element(By.ID,'add-document-class-select'))
        print("SELENIUM Document Class Selected")
        select.select_by_index(12)
        
        file_input=browser.find_element(By.ID, "filedata")
        file_input.send_keys("/home/ec2-user/EHR_Bots/"+str(filename))
        print("SELENIUM File uploaded")
        browser.save_screenshot("progress.png")
        print("SELENIUM Program Completed")
        select = Select(browser.find_element(By.ID,'add-document-class-select'))
        select.select_by_index(12)
        add_document_button=browser.find_element(By.XPATH,"/html/body/div[7]/div/div/div[2]/ul/li[3]/div[2]/div[2]/dl[5]/dd/button")
        add_document_button.click()
        time.sleep(20)
        add_document_button.click()
        time.sleep(30)
        browser.save_screenshot("completed.png")
        browser.close()
        browser.quit()
    except Exception as e:
        print("SELENIUM Errored: "+str(e))
        browser.save_screenshot("Errored_Screenshot.png")
        time.sleep(5)

        # sendEmail("nmathur@iph.ai", str(filename), "Errored_Screenshot.png", mrn)
        sendEmail("sgupta@iph.ai", str(filename), "Errored_Screenshot.png", mrn)
        sendEmail("nsabatini@iph.ai", str(filename), "Errored_Screenshot.png", mrn)





def add_file_piedmont(mrn, filename, count):
    login=get_secret_piedmont()
    
    print(login['username'])
    if count > 3:
        return "fuck you"
    
    
    print(f"SELENIUM {mrn}, {filename}, {count}")
    chromeOptions.add_argument('--ignore-certificate-errors')
    chromeOptions.add_argument('--allow-running-insecure-content')
    chromeOptions.headless = True
    browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chromeOptions)
    browser.set_window_size(1366, 768, browser.window_handles[0])

    try:
        browser.get("https://athenanet.athenahealth.com/1/77/login.esp")
        username=browser.find_element(By.ID, "USERNAME")
        username.send_keys(str(login['username']))
        password=browser.find_element(By.ID, "PASSWORD")
        password.send_keys(str(login['password']))
        login=browser.find_element(By.ID,"loginbutton")
        login.click()
        login=browser.find_element(By.ID,"loginbutton")
        login.click()
                


            
        login=browser.find_element(By.ID,"loginbutton")
        login.click()
                


        mrn=str(mrn)
        print("SELENIUM Switching to GlobalNav")
        time.sleep(4)
        browser.switch_to.frame("GlobalNav")
        
        
        search= browser.find_element(By.XPATH, '//*[@id="searchinput"]')
        search.send_keys(mrn)
        search.send_keys(Keys.RETURN)
        browser.switch_to.parent_frame()


        browser.switch_to.frame("GlobalWrapper")
        browser.switch_to.frame("frameContent")
        print("SELENIUM iframe switched to frame content")
        browser.switch_to.frame("frMain")
        print("SELENIUM iframe switched to frMain")
        print("SELENIUM Trying to navigate to the chart")
        
        quickview=browser.find_element(By.ID,'ActionMenu_Registration_span')
        quickview.click()
        chart=browser.find_element(By.XPATH,'//*[@id="ActionMenu_Registration"]/div[1]')
        chart.click()
        time.sleep(3)
        
        clinicals=browser.find_element(By.ID,'ActionMenu_Clinicals_span')
        clinicals.click()
        
        time.sleep(3)
        chart=browser.find_element(By.XPATH,'//*[@id="ActionMenu_Clinicals"]/div[1]')
        chart.click()
        time.sleep(3)
        browser.switch_to.default_content()
        print("SELENIUM Button clicked")

        count += 1

        
        print("SELENIUM uploading PDF")
        #wait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it(driver.find_element(By.XPATH, '//*[@id="GlobalWrapper"]')))
        time.sleep(3)

        browser.switch_to.frame("GlobalWrapper")
        browser.switch_to.frame("frameContent")
        print("SELENIUM iframe switched to frame content")
        browser.switch_to.frame("frMain")
        print("SELENIUM iframe switched to frMain")
        
        recent_test=browser.find_element(By.XPATH, '//*[@id="page-body"]/div[3]/div[8]/div[2]/div/div/div[2]/div/div/div[2]/ul/li[2]/button')
        recent_test.click()

        menu_toggle=browser.find_element(By.XPATH, '//*[@id="page-body"]/div[3]/div[6]/div[2]/div[1]/div/div')
        menu_toggle.click()
        add_documents=browser.find_element(By.XPATH, '/html/body/div[6]/div/div/div/ul/li[6]/div[1]')
        #add_documents=driver.find_element(By.LINK_TEXT, 'Add document')
        add_documents.click()
        time.sleep(5)
        toggle_upload=browser.find_element(By.XPATH, '/html/body/div[7]/div/div/div[2]/ul/li[3]/div[1]')
        toggle_upload.click()

        time.sleep(3)
        select = Select(browser.find_element(By.ID,'add-document-class-select'))
        print("SELENIUM Document Class Selected")
        select.select_by_index(12)
        file_input=browser.find_element(By.ID, "filedata")
        file_input.send_keys("/home/ec2-user/EHR_Bots/"+str(filename))
        print("SELENIUM File uploaded")
        select = Select(browser.find_element(By.ID,'add-document-class-select'))
        select.select_by_index(12)
        add_document_button=browser.find_element(By.XPATH,"/html/body/div[7]/div/div/div[2]/ul/li[3]/div[2]/div[2]/dl[5]/dd/button")
        add_document_button.click()
        time.sleep(20)
        add_document_button.click()
        time.sleep(10)
        print("SELENIUM Program Completed")
        browser.close()
        browser.quit()
    except:
        print("something broke")
        browser.save_screenshot(f"Errored_Screenshot{count}.png")
        add_file_piedmont(mrn, filename, count+1)



def add_file_INI(mrn, filename):
    login=get_secret_INI()
    try: 
        chromeOptions.add_argument('--ignore-certificate-errors')
        chromeOptions.add_argument('--allow-running-insecure-content')
        chromeOptions.headless = True
        browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chromeOptions)


        browser.set_window_size(2100, 1500, browser.window_handles[0])
        browser.get("https://login.advancedmd.com/")
        browser.switch_to.frame("frame-login")
        username_box= browser.find_element(By.XPATH ,'/html/body/div/div[2]/form/fieldset/div[1]/input')
        username_box.clear()
        username_box.send_keys(str(login['username']))


        password_box=browser.find_element(By.XPATH,'/html/body/div/div[2]/form/fieldset/div[2]/input')
        password_box.clear()
        password_box.send_keys(str(login['password']))

        officeKey_box= browser.find_element(By.XPATH ,'/html/body/div/div[2]/form/fieldset/div[3]/input')
        officeKey_box.clear()
        officeKey_box.send_keys(str(login['officekey']))

        print("SELENIUM_INI Added Credentials")
        action = ActionChains(browser)
        check_box = browser.find_element(By.XPATH ,'/html/body/div/div[2]/form/fieldset/div[5]/div[2]/input')

        action.move_to_element(check_box)
        action.click()
        action.perform()
        time.sleep(10)
        submit=browser.find_element(By.XPATH,'/html/body/div/div[2]/form/fieldset/div[6]/div/button')
        submit.click()
        print("SELENIUM_INI Logged in")
        time.sleep(10)
        try:
            snooze=browser.find_element(By.XPATH,'/html/body/div/amds-notifications/div[2]/button')
            snooze.click()
        except:
            print("SELENIUM_INI Snooze not required")
        whandle = browser.window_handles[1]
        browser.switch_to.window(whandle)
        print("SELENIUM_INI Window Switched")
        time.sleep(5)
        
        menu_button=browser.find_element(By.XPATH,'/html/body/amds-app/amds-ehr-shell/amds-ehr-shell-titlebar/div/div[2]/amds-global-menu/div/amds-menu-button/i')
        menu_button.click()
        chart_menu=browser.find_element(By.XPATH, '/html/body/amds-app/amds-ehr-shell/amds-ehr-shell-titlebar/div/div[2]/amds-global-menu/div/div/div/amds-topmenu-item[2]/div/div[1]/span')
        chart_menu.click()
        print("SELENIUM_INI Chart Menu Clicked")
        
        find_patient=browser.find_element(By.XPATH,'/html/body/amds-app/amds-ehr-shell/amds-ehr-shell-titlebar/div/div[2]/amds-global-menu/div/div/div/amds-topmenu-item[2]/div/div[2]/amds-submenu-item[2]/div/div[1]/span')
        find_patient.click()
        search=browser.find_element(By.XPATH, "/html/body/amds-app/amds-ehr-shell/amds-tab-set/section[1]/amds-patient-search/amds-ps-search-box/button")
        search.click()
        print("got to patient search page")
        time.sleep(5)
        
        iframe=browser.find_element(By.XPATH, '/html/body/amds-app/amds-ehr-shell/amds-tab-set/section[2]/amds-tab-view[2]/iframe')
        browser.switch_to.frame(iframe)
        
        print("switched to patient search frame")
        patient_field=browser.find_element(By.ID, 'txtPatientID')
        patient_field.send_keys(str(mrn))
        patient_field.send_keys(Keys.RETURN)
        print("Searched a patient")

        browser.switch_to.default_content()
        iframe=browser.find_element(By.XPATH, '/html/body/amds-app/amds-ehr-shell/amds-tab-set/section[2]/amds-tab-view[3]/iframe')
        browser.switch_to.frame(iframe)
        browser.set_window_size('1055', '906')

        browser.switch_to.frame("main") 
        print("swtiched to upload button")
        time.sleep(5)
        upload_button=browser.find_element(By.XPATH, '//*[@id="toolbar"]/li[6]')
        upload_button.click()

        
        browser.switch_to.frame("chartFrame1")
        browser.switch_to.frame("iframe")
    
        print("switched to chart frame")
        document_name=browser.find_element(By.XPATH, '//*[@id="txtName"]')
        document_name.send_keys(str(filename))

        file_input=browser.find_element(By.ID, "filUpload")
        file_input.send_keys("/home/ec2-user/EHR_Bots/"+str(filename))

        upload_submission_button=browser.find_element(By.XPATH, '//*[@id="btnUpload"]')
        upload_submission_button.click()
        print("SELENIUM_INI File is uploaded successfully")
        browser.save_screenshot(f"Errored_Screenshot_INI_1.png")
        time.sleep(10)
        alert = world.browser.switch_to.alert
        alert.accept()
        print("SELENIUM_INI was successful")
        browser.save_screenshot(f"Errored_Screenshot_INI_2.png")
        browser.close()
        browser.quit()
    except Exception as e:
        browser.save_screenshot(f"INI ERROR.png")
        print(e)


