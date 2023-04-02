#Import necessary modules
import datetime
import json
import requests
import tkinter as tk
import tkinter.messagebox as msgbox
from tkinter import colorchooser
from tkinter import ttk
from geopy.geocoders import Nominatim
from PIL import Image

class WeatherApp:
    def __init__(self, master=tk.Tk):
        #Set up the window's title, size, position, icon and background
        self.master = master
        self.master.title("Weather app")
        self.master.geometry("1080x720+420+180")
        self.master.iconbitmap("icon.ico")
        self.master["background"] = "grey20"
        self.master.protocol("WM_DELETE_WINDOW", self.save_and_quit)
        #Set up a font
        self.weather_font = ["Roboto", 17, "normal"]
        self.entry_font = ["Roboto", 17, "normal"]
        self.button_font = ["Roboto", 17, "bold"]
        #Set up the APIs by reading the api.txt file
        with open("api.txt", "r") as file:
            lines = file.readlines()
            if len(lines) < 2 or not lines[0].strip() or not lines[1].strip():
                msgbox.showerror("Error", "The api.txt file does not contain the required API keys. Please enter the keys and try again.")
                self.master.destroy()
                return
            self.weather_api = lines[0].strip()
            self.city_api = lines[1].strip()
        self.color_icon = tk.PhotoImage(file="color_icon.png")
        #Create widgets
        self.create_widgets()
            
    def create_widgets(self):
        """Create the widgets."""
        #Load the user's saved settings
        with open("settings.json", "r") as file:
            settings = json.load(file)
            city_name = settings["city"]
            background_color = settings["background_color"]
            font = settings["font"]
            font_size = settings["font_size"]
            time_format = settings["time_format"]
            temperature_unit = settings["temperature_unit"]
            pressure_unit = settings["pressure_unit"]
            file.close()
        self.master["background"] = background_color
        #Entry for the city name or code
        self.city_entry = tk.Entry(self.master, width=57, font=self.entry_font, justify=tk.CENTER,
                                   borderwidth=0, background="gray40")
        self.city_entry.place(relx=0.5, rely=0.075, anchor=tk.CENTER)
        self.city_entry.delete(0, tk.END)
        self.city_entry.insert(0, city_name)
        #Search button
        self.search_button = tk.Button(self.master, text="FETCH WEATHER DATA", font=self.button_font, 
                                       background="grey80", activebackground="grey60", 
                                       relief="flat", highlightthickness=0, borderwidth=0, 
                                       command=lambda: self.display_weather_data(city=self.city_entry.get(), 
                                                                                 temp_unit=self.temperature_dropdown.get(),
                                                                                 pressure_unit=self.pressure_dropdown.get(),
                                                                                 time_format=self.time_format_dropdown.get()))
        self.search_button.place(relx=0.42, rely=0.16, anchor=tk.CENTER)
        #Clear button
        self.clear_button = tk.Button(self.master, text="CLEAR", font=self.button_font, 
                                       background="grey80", activebackground="grey60", 
                                       relief="flat", highlightthickness=0, borderwidth=0, 
                                       command=self.clear)
        self.clear_button.place(relx=0.62, rely=0.16, anchor=tk.CENTER)
        #Create a frame for displaying weather data
        self.weather_frame = tk.Frame(self.master, width=800, height=400, background="gray30", 
                                      relief="solid")
        self.weather_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.weather_frame.pack_propagate(False)
        #Label for showing up the city's weather status
        self.weather_label = tk.Label(self.weather_frame, font=self.weather_font, background="gray30",
                                    foreground="SystemButtonFace")
        self.weather_label.pack(expand=True, fill="both", padx=20, pady=20)
        #Dropdown for selecting which temperature unit you want to be used
        temp_units = ["Celsius", "Fahrenheit", "Kelvin"]
        self.temperature_dropdown = ttk.Combobox(self.master, values=temp_units, style="TCombobox", font=self.button_font, width=14, 
                                                 state="readonly")
        if temperature_unit == "Celsius":
            self.temperature_dropdown.current(0)
        elif temperature_unit == "Fahrenheit":
            self.temperature_dropdown.current(1)
        else:
            self.temperature_dropdown.current(2)
        self.temperature_dropdown.place(relx=0.78, rely=0.87, anchor=tk.CENTER)
        #Dropdown for selecting which pressure unit you want to be used
        pressure_units = ["hPa", "PSI", "BAR", "ATM"]
        self.pressure_dropdown = ttk.Combobox(self.master, values=pressure_units, style="TCombobox", font=self.button_font, width=14, 
                                                 state="readonly")
        if pressure_unit == "hPa":
            self.pressure_dropdown.current(0)
        elif pressure_unit == "PSI":
            self.pressure_dropdown.current(1)
        elif pressure_unit == "BAR":
            self.pressure_dropdown.current(2)
        else:
            self.pressure_dropdown.current(3)
        self.pressure_dropdown.place(relx=0.78, rely=0.92, anchor=tk.CENTER)
        #Dropdown for selecting which format you want current time be displayed on
        time_formats = ["12h", "24h"]
        self.time_format_dropdown = ttk.Combobox(self.master, values=time_formats, style="TCombobox", font=self.button_font, width=4,
                                                 state="readonly")
        if time_format == "12h":
            self.time_format_dropdown.current(0)
        else:
            self.time_format_dropdown.current(1)
        self.time_format_dropdown.place(relx=0.63, rely=0.9, anchor=tk.CENTER)
        #Button for changing the background color
        self.change_background_color_button = tk.Button(self.master, image=self.color_icon, font=self.button_font, 
                                                        background="white", activebackground="grey80", 
                                                        relief="flat", highlightthickness=0, borderwidth=0, 
                                                        width=64, height=64, command=self.change_background_color)
        self.change_background_color_button.place(relx=0.16, rely=0.9, anchor=tk.CENTER)
        #Dropdown for changing the font
        fonts = ["Roboto", "Calibri", "Arial", "Times New Roman", "Consolas", "Courier"]
        self.font_dropdown = ttk.Combobox(self.master, values=fonts, style="TCombobox", font=self.button_font,
                                          width=14, state="readonly")
        self.button_font[0] = font
        self.entry_font[0] = font
        self.weather_font[0] = font
        if font == "Roboto":
            self.font_dropdown.current(0)
        elif font == "Calibri":
            self.font_dropdown.current(1)
        elif font == "Arial":
            self.font_dropdown.current(2)
        elif font == "Times New Roman":
            self.font_dropdown.current(3)
        elif font == "Consolas":
            self.font_dropdown.current(4)
        else:
            self.font_dropdown.current(5)
        self.font_dropdown.place(relx=0.31, rely=0.9, anchor=tk.CENTER)
        self.font_dropdown.bind("<<ComboboxSelected>>", self.change_font)
        #Spinbox for changing the size
        self.button_font[1] = font_size
        self.weather_font[1] = font_size
        self.entry_font[1] = font_size
        self.font_size_spinbox = tk.Spinbox(self.master, from_=5, to=50, width=3, font=self.button_font)
        self.font_size_spinbox.place(relx=0.44, rely=0.9, anchor=tk.CENTER)
        self.font_size_spinbox.delete(0, tk.END)
        self.font_size_spinbox.insert(0, int(self.button_font[1]))
        self.font_size_spinbox.bind("<KeyRelease>", self.change_font_size)
        self.font_size_spinbox.bind("<ButtonRelease>", self.change_font_size)
        #Button for resetting all settings
        self.reset_button = tk.Button(self.master, text="RESET", font=self.button_font, 
                                       background="white", activebackground="grey80", 
                                       relief="flat", highlightthickness=0, borderwidth=0, 
                                       command=self.reset)
        self.reset_button.place(relx=0.53, rely=0.9, anchor=tk.CENTER)
        #Update font and font size
        self.change_font()
        self.change_font_size()
    
    def display_weather_data(self, city:str, temp_unit:str, pressure_unit:str, time_format:str):
        """Display the weather in the label."""
        #Check if the city name is empty
        if city == "" or city.isspace():
            self.weather_label.config(text="Please insert a city.")
        else:
            weather_data = self.fetch_weather_data(city)
            city_data = self.get_city_info(city)
            #Check if the named city exists
            if city_data == "InvalidCityName":
                self.weather_label.config(text="City not found.")
                return "InvalidCityName"
            if weather_data["cod"] != "404":
                main_data = weather_data["main"]
                #Get the temperature
                if temp_unit == "Kelvin":
                    temperature = main_data["temp"]
                    temperature_unit = "°K"
                elif temp_unit == "Celsius":
                    temperature = main_data["temp"] - 273.15
                    temperature_unit = "°C"
                else:
                    temperature = round(((main_data["temp"] - 273.15)*9/5) + 32, 5)
                    temperature_unit = "°F"
                #Get the pressure
                if pressure_unit == "hPa":
                    pressure = main_data["pressure"]
                elif pressure_unit == "PSI":
                    pressure = round(main_data["pressure"]*0.0145, 5)
                elif pressure_unit == "BAR":
                    pressure = round(main_data["pressure"]*0.001, 5)
                else:
                    pressure = round(main_data["pressure"]*0.0009869233, 5)
                #Get the relative humidity, description, hour, minute, day, month, year, latitude, longitude, postal code and country of the city
                humidity = main_data["humidity"]
                weather_desc = weather_data["weather"][0]["description"]
                now = datetime.datetime.now()
                time = f"{str(now.hour).zfill(2)}:{str(now.minute).zfill(2)} {str(now.day).zfill(2)}/{str(now.month).zfill(2)}/{str(now.year).zfill(4)}"
                if time_format == "12h":
                    time_object = datetime.datetime.strptime(time, "%H:%M %d/%m/%Y")
                    formatted_time = time_object.strftime("%I:%M %p %d/%m/%Y")
                else:
                    formatted_time = time
                latitude, longitude = city_data["lat"], city_data["lng"]
                postal_code = city_data["postal_code"]
                country = city_data["country"]
                #Update the weather label
                self.weather_label.config(text=f"{city.capitalize()}, {postal_code}, {country}\n"
                                            f"X: {longitude}, Y: {latitude}\n"
                                            f"{formatted_time}\n"
                                            f"Temperature: {temperature:.2f}{temperature_unit}\n"
                                            f"Pressure: {pressure} {pressure_unit}\n"
                                            f"Humidity: {humidity}%\n"
                                            f"Observations: {weather_desc}")
            else:
                self.weather_label.config(text="City not found.")

    def fetch_weather_data(self, city:str) -> dict | str:
        """Fetch the weather data from OpenWeather."""
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        complete_url = f"{base_url}appid={self.weather_api}&q={city}"
        response = requests.get(complete_url)
        return response.json()
    
    def get_city_info(self, city:str) -> dict:
        """Get the city's information (county and postal code)."""
        #Get the latitude and longitude
        url = f"https://api.opencagedata.com/geocode/v1/json?q={city}&key={self.city_api}"
        response = requests.get(url).json()
        try:
            lat = response['results'][0]['geometry']['lat']
            lng = response['results'][0]['geometry']['lng']
        except IndexError:
            return "InvalidCityName"
        #Get the country and postal code
        geolocator = Nominatim(user_agent="user_agent")
        raw_info = geolocator.reverse(f"{lat}, {lng}")
        country = raw_info.address.split(", ")[-1]
        postal_code = raw_info.address.split(", ")[-2]
        return {"country": country, "postal_code":postal_code, "lat":lat, "lng":lng}

    def clear(self):
        """Clear the city entry and the weather data label."""
        self.city_entry.delete(0, tk.END)
        self.weather_label.config(text="")
    
    def change_background_color(self):
        """Prompt the user for a color and set it as background."""
        color = colorchooser.askcolor(title="Change background color")[1]
        if color:
            self.master["background"] = color
    
    def change_font(self, event=None):
        """Change the font of the widgets."""
        #Get the selected font from the font dropdown
        font_family = self.font_dropdown.get()
        #Change the font of the widgets
        self.weather_font[0] = font_family
        self.entry_font[0] = font_family
        self.button_font[0] = font_family
        self.city_entry.config(font=self.entry_font)
        self.search_button.config(font=self.button_font)
        self.clear_button.config(font=self.button_font)
        self.weather_label.config(font=self.weather_font)
        self.temperature_dropdown.config(font=self.button_font)
        self.pressure_dropdown.config(font=self.button_font)
        self.time_format_dropdown.config(font=self.button_font)
        self.font_dropdown.config(font=self.button_font)
    
    def change_font_size(self, event=None):
        """Change the font size of the widgets."""
        #Get the selected font size from the font dropdown
        
        try:
            font_size = self.font_size_spinbox.get()
            if font_size == "" or font_size.isspace():
                return "NoFontNumber"
            elif int(font_size) > 50:
                msgbox.showerror(title="Error", message="Font size can't be greater than 50!")
                return "TooBigFont"
            elif int(font_size) < 5:
                self.font_size_spinbox.delete(0, tk.END)
                self.font_size_spinbox.insert(0, 5)
                msgbox.showerror(title="Error", message="Font size can't be less than 5!")
                return "TooSmallFont"
            #Change the font size of the widgets
            self.weather_font[1] = font_size
            self.entry_font[1] = font_size
            self.button_font[1] = font_size
            self.city_entry.config(font=self.entry_font)
            self.search_button.config(font=self.button_font)
            self.clear_button.config(font=self.button_font)
            self.weather_label.config(font=self.weather_font)
            self.temperature_dropdown.config(font=self.button_font)
            self.pressure_dropdown.config(font=self.button_font)
            self.time_format_dropdown.config(font=self.button_font)
            self.font_dropdown.config(font=self.button_font)
            self.font_size_spinbox.config(font=self.button_font)
            self.reset_button.config(font=self.button_font)
        except (TypeError, ValueError, IndexError):
            self.font_size_spinbox.delete(0, tk.END)
            self.font_size_spinbox.insert(0, int(self.button_font[1]))
            msgbox.showerror(title="Error", message="Please insert a valid number between 5 and 50 (both inclusive)!")
            return "InvalidFontNumber"
    
    def reset(self):
        """Reset all settings."""
        #City entry
        self.city_entry.delete(0, tk.END)
        #Background
        self.master["background"] = "grey20"
        #Font
        self.button_font[0] = "Roboto"
        self.entry_font[0] = "Roboto"
        self.weather_font[0] = "Roboto"
        self.font_dropdown.current(0)
        self.change_font()
        #Font size
        self.button_font[1] = 17
        self.entry_font[1] = 17
        self.weather_font[1] = 17
        self.font_size_spinbox.delete(0, tk.END)
        self.font_size_spinbox.insert(0, 17)
        self.change_font_size()
        #Time format
        self.time_format_dropdown.current(1)
        #Temperature unit
        self.temperature_dropdown.current(0)
        #Pressure unit
        self.pressure_dropdown.current(0)
    
    def save_and_quit(self):
        """Save the settings to a file, to load them later."""
        #Save the settings
        settings = {
            "city": self.city_entry.get(),
            "background_color": self.master["background"],
            "font": self.button_font[0],
            "font_size": self.button_font[1],
            "time_format": self.time_format_dropdown.get(),
            "temperature_unit": self.temperature_dropdown.get(),
            "pressure_unit": self.pressure_dropdown.get()
        }
        #Write them in a file
        with open('settings.json', 'w') as file:
            json.dump(settings, file)
            file.close()
        #Close the window
        self.master.destroy()

#Create a window and run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(master=root)
    app.master.mainloop()