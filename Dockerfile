FROM python:3.6.1
RUN git clone https://github.com/Unitec-Segebre/LenguajesDeProgramacion_Tarea2.git
EXPOSE 8080
CMD cd /LenguajesDeProgramacion_Tarea2 && python tarea2.py
