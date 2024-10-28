import pygame
from pygame.locals import *
import random
import threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

pygame.init()

# Configuración de pantalla
width = 500
height = 500
screen_size = (width, height)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Car Game')

# Colores
gray = (100, 100, 100)
green = (76, 208, 56)
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (255, 232, 0)

# Tamaños de la carretera y líneas
road_width = 300
marker_width = 10
marker_height = 50

# Carriles
left_lane = 150
center_lane = 250
right_lane = 350
lanes = [left_lane, center_lane, right_lane]

# Marcadores de borde
road = (100, 0, road_width, height)
left_edge_marker = (95, 0, marker_width, height)
right_edge_marker = (395, 0, marker_width, height)

# Posición inicial del jugador
player_x = 250
player_y = 400

# Configuración de frame y velocidad
clock = pygame.time.Clock()
fps = 120
speed = 2
score = 0
gameover = False
pregunta_mostrada = False  # Variable para pausar el juego

# Temporizador para las preguntas (20 segundos)
question_interval = 20000  # 20 segundos en milisegundos
last_question_time = pygame.time.get_ticks()

# Preguntas y respuestas
preguntas = [
    {
        "texto": "¿Qué significa una señal de alto?",
        "imagen": "images/alto.jpg",
        "opciones": ["A) Detenerse", "B) Continuar", "C) Ceder el paso"],
        "respuesta_correcta": "A) Detenerse"
    },
    {
        "texto": "¿Qué significa la luz verde en un semáforo?",
        "imagen": "images/semaforo_verde.jpg",
        "opciones": ["A) Avanzar", "B) Detenerse", "C) Reducir velocidad"],
        "respuesta_correcta": "A) Avanzar"
    },
    {
        "texto": "¿Qué significa una señal de ceder el paso?",
        "imagen": "images/ceder_paso.jpg",
        "opciones": ["A) Continuar sin detenerse", "B) Detenerse y ceder el paso", "C) Acelerar"],
        "respuesta_correcta": "B) Detenerse y ceder el paso"
    },
    {
        "texto": "¿Cuál es el límite de velocidad en una zona escolar?",
        "imagen": "images/zona_escolar.jpg",
        "opciones": ["A) 50 km/h", "B) 30 km/h", "C) 20 km/h"],
        "respuesta_correcta": "B) 30 km/h"
    },
    {
        "texto": "¿Qué debes hacer al acercarte a un semáforo en rojo?",
        "imagen": "images/semaforo_rojo.jpg",
        "opciones": ["A) Detenerse", "B) Acelerar", "C) Continuar"],
        "respuesta_correcta": "A) Detenerse"
    },
    # Agrega más preguntas aquí si lo deseas
]

# Función para mostrar preguntas en un hilo separado
def mostrar_pregunta():
    global gameover, pregunta_mostrada
    pregunta = random.choice(preguntas)
    pregunta_mostrada = True  # Pausa el juego al mostrar la pregunta
    ventana = tk.Tk()
    ventana.title("Pregunta de Educación Vial")
    ventana.geometry("400x400")
    
    # Posicionar la ventana de preguntas al lado del juego
    x_offset = 520  # Desplazamiento a la derecha
    y_offset = 100   # Desplazamiento hacia abajo
    ventana.geometry(f"400x400+{x_offset}+{y_offset}")

    ventana.resizable(False, False)

    # Muestra la pregunta y opciones
    pregunta_label = tk.Label(ventana, text=pregunta["texto"], font=("Arial", 14), wraplength=300)
    pregunta_label.pack(pady=10)
    
    img = Image.open(pregunta["imagen"])
    img = img.resize((200, 100))
    img = ImageTk.PhotoImage(img)
    imagen_label = tk.Label(ventana, image=img)
    imagen_label.image = img
    imagen_label.pack()

    # Función para verificar la respuesta
    def verificar_respuesta(opcion):
        nonlocal ventana
        global gameover, pregunta_mostrada
        if opcion == pregunta["respuesta_correcta"]:
            messagebox.showinfo("Correcto", "¡Respuesta correcta! Continúa jugando.")
        else:
            messagebox.showerror("Incorrecto", "Respuesta incorrecta. ¡Juego terminado!")
            gameover = True
        ventana.destroy()
        pregunta_mostrada = False  # Reanuda el juego

    # Botones de opciones
    for opcion in pregunta["opciones"]:
        tk.Button(ventana, text=opcion, command=lambda opcion=opcion: verificar_respuesta(opcion)).pack(pady=5)

    ventana.mainloop()

# Clase del vehículo
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        image_scale = 45 / image.get_rect().width
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        self.image = pygame.transform.scale(image, (new_width, new_height))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

class PlayerVehicle(Vehicle):
    def __init__(self, x, y):
        image = pygame.image.load('images/car.png')
        super().__init__(image, x, y)

# Grupos de sprites
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()

# Crea el auto del jugador
player = PlayerVehicle(player_x, player_y)
player_group.add(player)

# Cargar imágenes de vehículos
image_filenames = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']
vehicle_images = [pygame.image.load('images/' + image) for image in image_filenames]

# Cargar imagen de choque
crash = pygame.image.load('images/crash.png')
crash_rect = crash.get_rect()

# Bucle principal del juego
running = True
while running:
    clock.tick(fps)

    # Solo muestra la pregunta después de un tiempo inicial de juego
    current_time = pygame.time.get_ticks()
    if not pregunta_mostrada and (current_time - last_question_time >= question_interval):
        last_question_time = current_time
        hilo_pregunta = threading.Thread(target=mostrar_pregunta)
        hilo_pregunta.start()

    # Continúa el juego si no hay una pregunta abierta
    if not pregunta_mostrada:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_LEFT and player.rect.center[0] > left_lane:
                    player.rect.x -= 100
                elif event.key == K_RIGHT and player.rect.center[0] < right_lane:
                    player.rect.x += 100

        # Renderizar fondo y objetos
        screen.fill(green)
        pygame.draw.rect(screen, gray, road)
        pygame.draw.rect(screen, yellow, left_edge_marker)
        pygame.draw.rect(screen, yellow, right_edge_marker)

        # Animación de las líneas de los carriles
        lane_marker_move_y = (current_time // 5) % marker_height * 2
        for y in range(marker_height * -2, height, marker_height * 2):
            pygame.draw.rect(screen, white, (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
            pygame.draw.rect(screen, white, (center_lane + 45, y + lane_marker_move_y, marker_width, marker_height))

        player_group.draw(screen)

        # Agregar vehículos
        if len(vehicle_group) < 2:
            add_vehicle = True
            for vehicle in vehicle_group:
                if vehicle.rect.top < vehicle.rect.height * 1.5:
                    add_vehicle = False
            if add_vehicle:
                lane = random.choice(lanes)
                image = random.choice(vehicle_images)
                vehicle = Vehicle(image, lane, height / -2)
                vehicle_group.add(vehicle)

        # Mover los vehículos
        for vehicle in vehicle_group:
            vehicle.rect.y += speed
            
            # Eliminar vehículo una vez que sale de la pantalla
            if vehicle.rect.top >= height:
                vehicle.kill()
                score += 1  # Incrementar puntaje
                if score > 0 and score % 5 == 0:
                    speed += 0.5  # Aumentar velocidad cada 5 puntos

        vehicle_group.draw(screen)

        # Mostrar puntaje
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render('Score: ' + str(score), True, white)
        text_rect = text.get_rect()
        text_rect.center = (50, 400)
        screen.blit(text, text_rect)

        # Verificar colisiones
        if pygame.sprite.spritecollide(player, vehicle_group, True):
            gameover = True
            crash_rect.center = [player.rect.center[0], player.rect.top]

        # Mostrar fin de juego
        if gameover:
            screen.blit(crash, crash_rect)
            pygame.draw.rect(screen, red, (0, 50, width, 100))
            font = pygame.font.Font(pygame.font.get_default_font(), 16)
            text = font.render('Game over. Play again? (Enter Y or N)', True, white)
            text_rect = text.get_rect()
            text_rect.center = (width / 2, 100)
            screen.blit(text, text_rect)

    # Actualiza la pantalla
    pygame.display.update()

    # Esperar input del usuario para reiniciar o salir
    while gameover:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == QUIT:
                gameover = False
                running = False
            if event.type == KEYDOWN:
                if event.key == K_y:
                    gameover = False
                    speed = 2
                    score = 0
                    vehicle_group.empty()
                    player.rect.center = [player_x, player_y]
                elif event.key == K_n:
                    gameover = False
                    running = False

pygame.quit()