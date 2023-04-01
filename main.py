#Import necessary modules
import datetime
import requests
import tkinter as tk
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
        #Set up a font
        self.weather_font = ("Roboto", 20, "normal")
        self.entry_font = ("Roboto", 20, "normal")
        self.button_font = ("Roboto", 15, "bold")
        #Set up the APIs by reading the api.txt file
        with open("api.txt", "r") as file:
            text = file.read()
            self.weather_api = text.split("\n")[0]
            self.city_api = text.split("\n")[1]
            file.close()
        #Load the color icon image
        self.color_icon = tk.PhotoImage(file="color_icon.png")
        #Create widgets
        self.create_widgets()
            
    def create_widgets(self):
        """Create the widgets."""
        #Entry for the city name or code
        self.city_entry = tk.Entry(self.master, width=57, font=self.entry_font, justify=tk.CENTER,
                                   borderwidth=0, background="gray40")
        self.city_entry.place(relx=0.5, rely=0.075, anchor=tk.CENTER)
        #Search button
        self.search_button = tk.Button(self.master, text="FETCH WEATHER DATA", font=self.button_font, 
                                       background="grey80", activebackground="grey60", 
                                       relief="flat", highlightthickness=0, borderwidth=0, 
                                       command=lambda: self.display_weather_data(city=self.city_entry.get(), 
                                                                                 temp_unit=self.temperature_dropdown.get(),
                                                                                 pressure_unit=self.pressure_dropdown.get(),
                                                                                 time_format=self.time_format_dropdown.get()))
        self.search_button.place(relx=0.5, rely=0.16, anchor=tk.CENTER)
        #Clear button
        self.clear_button = tk.Button(self.master, text="CLEAR", font=self.button_font, 
                                       background="grey80", activebackground="grey60", 
                                       relief="flat", highlightthickness=0, borderwidth=0, 
                                       command=self.clear)
        self.clear_button.place(relx=0.9, rely=0.9, anchor=tk.CENTER)
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
        self.temperature_dropdown.current(0)
        self.temperature_dropdown.place(relx=0.75, rely=0.9, anchor=tk.CENTER)
        #Dropdown for selecting which pressure unit you want to be used
        pressure_units = ["hPa", "PSI", "BAR", "ATM"]
        self.pressure_dropdown = ttk.Combobox(self.master, values=pressure_units, style="TCombobox", font=self.button_font, width=14, 
                                                 state="readonly")
        self.pressure_dropdown.current(0)
        self.pressure_dropdown.place(relx=0.55, rely=0.9, anchor=tk.CENTER)
        #Dropdown for selecting which format you want current time be displayed on
        time_formats = ["12h", "24h"]
        self.time_format_dropdown = ttk.Combobox(self.master, values=time_formats, style="TCombobox", font=self.button_font, width=4,
                                                 state="readonly")
        self.time_format_dropdown.current(1)
        self.time_format_dropdown.place(relx=0.4, rely=0.9, anchor=tk.CENTER)
        #Button for changing the background color
        self.change_background_color_button = tk.Button(self.master, image=self.color_icon, font=self.button_font, 
                                                        background="grey80", activebackground="grey60", 
                                                        relief="flat", highlightthickness=0, borderwidth=0, 
                                                        width=64, height=64, command=self.change_background_color)
        self.change_background_color_button.place(relx=0.07, rely=0.9, anchor=tk.CENTER)
    
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

#Create a window and run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(master=root)
    app.master.mainloop()