import subprocess

subprocess.Popen('pip install selenium --user',shell=True)

import json
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as cond
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import selenium.common.exceptions as excepts
from time import sleep
from tkinter import Tk,Label,StringVar,BooleanVar,Checkbutton,Button,Entry,Text
import random

class app():

    def __init__(self):
        self.window = Tk()
        self.window.geometry('500x500')
        self.window.title('LIBRUSReader')

        loginLabel = Label(text='Podaj login')
        passwordLabel = Label(text='Podaj hasło')
        loginLabel.place(x= 10, y= 25)
        passwordLabel.place(x=10, y= 50)

        self.login = StringVar()
        self.password = StringVar()
        self.windowMode = BooleanVar()
        self.consoleReadingMessages = BooleanVar()
        self.answer = StringVar()

        loginEntry = Entry(textvariable = self.login, width = '30')
        passwordEntry = Entry(textvariable = self.password, width = '30')
        loginEntry.place(x = 80, y = 25)
        passwordEntry.place(x = 80, y = 50)

        checkbox = Checkbutton(self.window,text='Tryb okienkowy',variable=self.windowMode)
        checkbox.place(x = 15, y = 125)

        checkboxOdczyt = Checkbutton(self.window,text='Wyświetlanie wiadomości w konsoli (użyteczne przy wyłączeniu trybu okienkowego',variable=self.consoleReadingMessages)
        checkboxOdczyt.place(x = 15, y = 150)

        self.answer = Text(self.window,width='54',height='15')
        answerLabel = Label(text='Odpowiedź do wiadomości (jeśli puste, nie przesyła)')
        self.answer.place(x = 15, y = 215)
        answerLabel.place(x = 15, y = 190)

        runProgram = Button(self.window, text = 'Uruchom program', width = '36', height = ' 1', command = self.zapiszDane,bg='grey')
        runProgram.place(x=16, y = 100)
        self.window.mainloop()
        
    def zapiszDane(self):
        data = {'login':self.login.get(),'password':self.password.get(),'windowMode':self.windowMode.get(),'consoleReadingMessages':self.consoleReadingMessages.get(),'answer':self.answer.get('1.0','end-1c')}
        with open('config.json','w') as f:
            json.dump(data,f)
        self.window.destroy()


class bot(app):

    def signIn(self):

        link = self.browser.current_url
        wait(self.browser,10).until(cond.frame_to_be_available_and_switch_to_it((By.ID,'caLoginIframe')))
        loginInput = self.browser.find_element_by_xpath('//*[@id="Login"]')
        loginInput.send_keys(self.config['login'])
        passwordInput = self.browser.find_element_by_xpath('//*[@id="Pass"]')
        passwordInput.send_keys(self.config['password'])
        self.browser.find_element_by_xpath('//*[@id="LoginBtn"]').click()
        link2 = self.browser.current_url
        if link != link2:
            print('Zalogowałem się')
        else:
            print('Logowanie nie udało się')

    def checkingIfMessagesExist(self):

        self.browser.switch_to.default_content()
        sleep(6)
        self.browser.find_element_by_id('icon-wiadomosci').click()
        print('Przechodzę do wiadomości')
        wait(self.browser,10).until(cond.visibility_of_element_located((By.XPATH,'/html/body/div[3]/div[3]/form/div/div/table/tbody/tr/td[2]/table[2]')))

        if self.browser.find_element_by_id('cookieBoxClose'):
            self.browser.find_element_by_id('cookieBoxClose').click()
        try:
            while self.browser.find_element_by_partial_link_text('Następna'):
                self.browser.find_element_by_partial_link_text('Następna').click()
        except excepts.NoSuchElementException:
            try:
                while self.browser.find_element_by_partial_link_text('Poprzednia'):
                    messagesBody = self.browser.find_element_by_xpath(("//table[@class='decorated stretch']/tbody"))
                    messages = messagesBody.find_elements_by_xpath("//tr/td[@style = 'font-weight: bold;']/a")
                    if len(messages) >0:
                        print('Są wiadomości, czytam...')
                        while len(messages) > 0:
                            self.readingMessages(messages)
                        self.browser.find_element_by_partial_link_text('Poprzednia').click()
                    else:
                        print('Nie ma wiadomości')
                        self.browser.find_element_by_partial_link_text('Poprzednia').click()
            except excepts.NoSuchElementException:
                while True:
                    messagesBody = self.browser.find_element_by_xpath(("//table[@class='decorated stretch']/tbody"))
                    messages = messagesBody.find_elements_by_xpath("//tr/td[@style = 'font-weight: bold;']/a")
                    if len(messages) > 0:  
                        print('Są wiadomości czytam')
                        self.readingMessages(messages)
                    else:
                        czas = random.randrange(30,120)
                        print(f'Nie ma wiadomości, czekam {czas} sekund i odświeżam')
                        sleep(czas)
                        self.browser.find_element_by_id('icon-wiadomosci').click()
        
    def readingMessages(self,messages):
        for message in reversed(messages):
            wait(self.browser,10).until(cond.visibility_of_element_located((By.XPATH,'/html/body/div[3]/div[3]/form/div/div/table/tbody/tr/td[2]/table[2]')))
            message.click()
            if self.config['consoleReadingMessages']:
                print('_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _')
                for i in range(3):
                    print('\n')
                    topic = self.browser.find_elements_by_xpath("//td[@class='left']")
                    print('\t'+topic[i].text+'\n')
                lyrics = self.browser.find_element_by_xpath('/html/body/div[3]/div[3]/form/div/div/table/tbody/tr/td[2]/div')
                print(lyrics.text+'\n','_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _')
                self.browser.find_element_by_xpath('/html/body/div[3]/div[3]/form/div/div/table/tbody/tr/td[2]/table[1]/tbody/tr/td/input[4]').click() 
            if len(self.config['answer'])>0:
                print('Odpisuję...\n',self.config['answer'])
                self.browser.find_element_by_xpath('/html/body/div[3]/div[3]/form/div/div/table/tbody/tr/td[2]/table[1]/tbody/tr/td/input[2]').click()
                sleep(3)
                textArea = self.browser.find_element_by_tag_name('textarea')
                textArea.click().clear()
                textArea.send_keys(self.config['answer'])
                sleep(3)
                self.browser.find_element_by_xpath('/html/body/div[3]/div[3]/form/div/div/table/tbody/tr[8]/td[2]/input[1]').click()
                sleep(5)
                self.browser.find_element_by_partial_link_text('odebrane').click()
                print('Wracam do czytania')
            messagesBody = self.browser.find_element_by_xpath(("//table[@class='decorated stretch']/tbody"))
            messages = messagesBody.find_elements_by_xpath("//tr/td[@style = 'font-weight: bold;']/a")        

    def __init__(self):
        try:
            with open('config.json','r') as f:
                self.config = json.load(f)
            if self.config['windowMode']:        
                self.browser = webdriver.Firefox(executable_path=r'.\geckodriver.exe')

            else:
                self.browser = webdriver.Firefox(executable_path=r'.\geckodriver.exe',options = Options().add_argument('-headless'))
            
            print('Otwieram stronę')
            self.browser.get('https://portal.librus.pl/rodzina')
            print('Otworzyłem stronę')
            wait(self.browser,10).until(cond.element_to_be_clickable((By.XPATH,'/html/body/nav/div/div[1]/div/div[2]/a[3]'))).click()
            wait(self.browser,10).until(cond.element_to_be_clickable((By.XPATH,'/html/body/nav/div/div[1]/div/div[2]/div/a[2]'))).click()
            self.signIn()
            self.checkingIfMessagesExist()
        except KeyboardInterrupt:
            self.browser.quit()

if os.path.isfile('config.json'):
    print('Rozpoczynam program, jesli chcesz zakonczyc wcisnij CTRL+C'+'\n'+'\n')
    bot()
else:
    print('Rozpoczynam program, jesli chcesz zakonczyc wcisnij CTRL+C'+'\n'+'\n')
    app()
    bot()













# if len(self.messages) >= 1:
        #     print('Są wiadomości, czytam...')



        # if len(self.browser.find_elements_by_partial_link_text('Następna'))>0:
        #     self.browser.find_element_by_partial_link_text('Następna').click()

        #     if len(self.browser.find_elements_by_partial_link_text('Następna'))>0:
        #         self.browser.find_element_by_partial_link_text('Następna').click()
        #         self.wiadomosci = self.browser.find_element_by_xpath(("//table[@class='decorated stretch']/tbody"))
        #         print('Sprawdzam trzecią stronę')
        #         if len(self.wiadomosci.find_elements_by_xpath("//tr/td[@style = 'font-weight: bold;']/a"))>=1:
        #             print("Są wiadomości, czytam...")
        #             self.czytanieWiadomosci()
        #             self.browser.find_element_by_partial_link_text('Poprzednia').click()
        #         else:
        #             print('Nie ma wiadomości')
        #     else:
        #         print('Sprawdzam drugą stronę')
        #         self.wiadomosci = self.browser.find_element_by_xpath(("//table[@class='decorated stretch']/tbody"))
        #         if len(self.wiadomosci.find_elements_by_xpath("//tr/td[@style = 'font-weight: bold;']/a"))>=1:
        #             print("Są wiadomości, czytam...")
        #             self.czytanieWiadomosci()
        #             self.browser.find_element_by_partial_link_text('Poprzednia').click()
        #         else:
        #             print('Nie ma wiadomości')
        #             self.browser.find_element_by_partial_link_text('Poprzednia').click()
        #             #self.wiadomosci = self.browser.find_element_by_xpath(("//table[@class='decorated stretch']/tbody"))
        #             print('Wracam na pierwszą stronę')
        #             while True:
        #                 self.wiadomosci = self.browser.find_element_by_xpath(("//table[@class='decorated stretch']/tbody"))
        #                 if len(self.wiadomosci.find_elements_by_xpath('//tr/td[@style="font-weight: bold;"]/a'))>=1:
        #                     print("Są wiadomości, czytam...")
        #                     self.czytanieWiadomosci()
        #                 else:
        #                     self.czas = random.randrange(30,120)                    
        #                     print('Nie ma wiadomosci, czekam {} sekund i odświeżam.'.format(self.czas))
        #                     sleep(self.czas)
        #                     self.browser.find_element_by_id('icon-wiadomosci').click()
        # else:
        #     while True:
        #         self.wiadomosci = self.browser.find_element_by_xpath(("//table[@class='decorated stretch']/tbody"))
        #         if len(self.wiadomosci.find_elements_by_xpath('//tr/td[@style="font-weight: bold;"]/a'))>=1:
        #             print("Są wiadomości, czytam...")
        #             self.czytanieWiadomosci()
        #         else:
        #             self.czas = random.randrange(30,120)                    
        #             print('Nie ma wiadomosci, czekam {} sekund i odświeżam.'.format(self.czas))
        #             sleep(self.czas)
        #             self.browser.find_element_by_id('icon-wiadomosci').click()


# self.wiadomosci = self.browser.find_element_by_xpath("//table[@class='decorated stretch']/tbody")
            # self.lista = self.wiadomosci.find_elements_by_xpath('//tr/td[@style="font-weight: bold;"]/a')
            # self.lista[i].click()
    
# else:
            #     sleep(5)
            #     self.browser.find_element_by_xpath('/html/body/div[3]/div[3]/form/div/div/table/tbody/tr/td[2]/table[1]/tbody/tr/td/input[4]').click()    

# options = Options()
                # options.add_argument('-headless')