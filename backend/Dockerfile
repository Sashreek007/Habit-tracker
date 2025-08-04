#Using a light version of python image

FROM python:3.10-slim


#Set working dir in the image

WORKDIR /app

#copy all the backends files into the container

COPY . .

# Install all the required packages
RUN pip install --no-cache-dir -r requirements.txt

# EXPOSE  port for streamlit 
EXPOSE 5000

# Start the Streamlit app
CMD ["python", "app.py"]
