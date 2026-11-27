
Funcion n <- Formacion(x0, x1, prof)
	Si prof = 0 O (x1 - x0) < 60 Entonces
		n <- 1
	SiNo
		n <- Formacion(x0, (x0 + x1) / 2, prof - 1) + Formacion((x0 + x1) / 2, x1, prof - 1)
	FinSi
FinFuncion


Funcion n <- DisparoFractal(prof)
	Si prof = 0 Entonces
		n <- 1
	SiNo
		n <- 1 + DisparoFractal(prof - 1) + DisparoFractal(prof - 1)
	FinSi
FinFuncion


SubProceso Explosion(n)
	Si n > 0 Entonces
		Escribir Sin Saltar "*"
		Explosion(n - 1)
	SiNo
		Escribir ""
	FinSi
FinSubProceso


SubProceso Musica(tema, sonido)
	Si sonido Entonces
		Escribir "  [MUSICA] Sonando tema: ", tema
	FinSi
FinSubProceso


Funcion opc <- MenuPausa(sonido, tema)
	Definir opc Como Entero
	Si sonido Entonces
		Escribir "  [MUSICA] Pausada"
	FinSi
	Escribir "======== PAUSA ========"
	Escribir "1. Continuar"
	Escribir "2. Salir al inicio"
	Escribir "3. Salir del juego"
	Leer opc
	Si opc = 1 Y sonido Entonces
		Escribir "  [MUSICA] Reanudada: ", tema
	FinSi
FinFuncion

Algoritmo NovaDefender
	Definir skins, difs, nombreJefe Como Caracter
	Dimension skins[5], difs[3], nombreJefe[3]
	skins[1] <- "Cian clasica"; skins[2] <- "Fenix rojo"; skins[3] <- "Rayo dorado"
	skins[4] <- "Sombra violeta"; skins[5] <- "Hielo blanco"
	difs[1] <- "Basico"; difs[2] <- "Intermedio"; difs[3] <- "Dificil"
	nombreJefe[1] <- "Jefe AMARILLO"; nombreJefe[2] <- "Jefe ROJO"; nombreJefe[3] <- "Jefe NEGRO de ojos rojos"
	Definir skin, dif, opc, nivel, vidas, puntos, misiles, triple, escudo, enemigos, hpJefe, balas, dano, premio Como Entero
	Definir sonido, salir, jugando, enJefe Como Logico
	skin <- 1; dif <- 2; sonido <- Verdadero; salir <- Falso

	Mientras No salir Hacer
		Musica("menu", sonido)
		Escribir "=============================="
		Escribir "        DEFENSOR GALACTICO"
		Escribir "=============================="
		Escribir "1. START"
		Escribir "2. Dificultad: ", difs[dif]
		Escribir "3. Nave: ", skins[skin]
		Escribir "4. Sonido: ", sonido
		Escribir "5. Salir del juego"
		Leer opc
		Segun opc Hacer
			2: dif <- dif MOD 3 + 1
			3: skin <- skin MOD 5 + 1
			4: sonido <- No sonido
			5: salir <- Verdadero
			1:
				vidas <- 3; puntos <- 0; misiles <- 0; triple <- 0; escudo <- 0
				nivel <- 1; jugando <- Verdadero
				Mientras jugando Y nivel <= 3 Hacer
					enemigos <- Formacion(40, 440, 1 + nivel)
					enJefe <- Falso
					Musica("batalla", sonido)
					Escribir "--- NIVEL ", nivel, " (", difs[dif], ") - ", enemigos, " enemigos ---"
					Mientras jugando Y (enemigos > 0 O enJefe) Hacer
						Escribir "Vidas: ", vidas, " | Puntos: ", puntos, " | Misiles: ", misiles, " | Triple: ", triple, " | Escudo: ", escudo
						Si enJefe Entonces
							Escribir nombreJefe[nivel], " - Vida: ", hpJefe
						SiNo
							Escribir "Enemigos restantes: ", enemigos
						FinSi
						Escribir "1 Disparar  2 Misil  3 Esquivar  0 Pausa"
						Leer opc
						Si opc = 0 Entonces
							opc <- MenuPausa(sonido, "batalla")
							Si opc = 2 Entonces
								jugando <- Falso
							FinSi
							Si opc = 3 Entonces
								jugando <- Falso; salir <- Verdadero
							FinSi
						SiNo
							dano <- 0
							Si opc = 1 Entonces
								dano <- 1
								Si triple > 0 Entonces
									dano <- 3; triple <- triple - 1
								FinSi
							FinSi
							Si opc = 2 Entonces
								Si misiles > 0 Entonces
									misiles <- misiles - 1; dano <- 5
									Escribir "  >>==> Misil teledirigido lanzado"
								SiNo
									Escribir "  No tienes misiles"
								FinSi
							FinSi
							Si enJefe Entonces
								hpJefe <- hpJefe - dano * 4
								Si hpJefe <= 0 Entonces
									Escribir "¡", nombreJefe[nivel], " destruido!"
									Explosion(20)
									puntos <- puntos + 1000 * nivel
									vidas <- vidas + 1
									Escribir "  El jefe solto: CORAZON (+1 vida) y MISILES"
									misiles <- misiles + 3
									enJefe <- Falso
								FinSi
							SiNo
								Si dano > enemigos Entonces
									dano <- enemigos
								FinSi
								Si dano > 0 Entonces
									enemigos <- enemigos - dano; puntos <- puntos + 100 * dano
									Explosion(5)
									Si Aleatorio(1, 100) <= 12 Entonces
										premio <- Aleatorio(1, 4)
										Segun premio Hacer
											1: vidas <- vidas + 1; Escribir "  Premio: CORAZON (+1 vida)"
											2: misiles <- misiles + 3; Escribir "  Premio: MISILES (+3)"
											3: triple <- triple + 5; Escribir "  Premio: DISPARO TRIPLE"
											4: escudo <- 1; Escribir "  Premio: ESCUDO"
										FinSegun
									FinSi
								FinSi
								Si enemigos = 0 Entonces
									enJefe <- Verdadero
									hpJefe <- 20 * nivel * dif
									Escribir "!!! ALERTA: aparece el ", nombreJefe[nivel], " !!!"
									Musica("jefe", sonido)
								FinSi
							FinSi
							// ataque enemigo
							Si enJefe Entonces
								balas <- DisparoFractal(nivel)
							SiNo
								balas <- 1
							FinSi
							Si enJefe O enemigos > 0 Entonces
								Si opc <> 3 Y Aleatorio(1, 100) <= 15 * dif + balas Entonces
									Si escudo > 0 Entonces
										escudo <- 0; Escribir "  El escudo te protegio"
									SiNo
										vidas <- vidas - 1; Escribir "  ¡Te dieron! (", balas, " balas)"
										Si vidas <= 0 Entonces
											jugando <- Falso
											Escribir "===== GAME OVER ===== Puntos: ", puntos
										FinSi
									FinSi
								FinSi
							FinSi
						FinSi
					FinMientras
					Si jugando Entonces
						nivel <- nivel + 1
					FinSi
				FinMientras
				Si nivel > 3 Entonces
					Escribir "***** ¡VICTORIA! Salvaste la galaxia. Puntos: ", puntos, " *****"
				FinSi
			De Otro Modo:
				Escribir "Opcion no valida"
		FinSegun
	FinMientras
	Escribir "Gracias por jugar Defensor Galactico"
FinAlgoritmo
