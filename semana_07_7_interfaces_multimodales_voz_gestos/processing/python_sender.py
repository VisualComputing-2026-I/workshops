from pythonosc.udp_client import SimpleUDPClient


OSC_HOST = "127.0.0.1"
OSC_PORT = 12000


def print_help() -> None:
    print("Comandos disponibles:")
    print("  color <rojo|verde|azul|amarillo|naranja|morado|rosa|cian|blanco|negro>")
    print("  shape <circulo|cuadrado|triangulo|estrella>")
    print("  anim <start|stop|toggle>")
    print("  text <mensaje>")
    print("  salir")


def main() -> None:
    client = SimpleUDPClient(OSC_HOST, OSC_PORT)

    print(f"Enviando OSC a {OSC_HOST}:{OSC_PORT}")
    print_help()

    while True:
        raw = input("\n> ").strip()
        if not raw:
            continue

        if raw.lower() in {"salir", "exit", "quit"}:
            print("Cerrando emisor.")
            break

        command, _, argument = raw.partition(" ")
        command = command.lower()
        argument = argument.strip()

        if command == "color" and argument:
            client.send_message("/color", argument)
            print(f"Enviado: /color {argument}")
        elif command == "shape" and argument:
            client.send_message("/shape", argument)
            print(f"Enviado: /shape {argument}")
        elif command == "anim" and argument:
            client.send_message("/anim", argument)
            print(f"Enviado: /anim {argument}")
        elif command == "text" and argument:
            client.send_message("/text", argument)
            print(f"Enviado: /text {argument}")
        else:
            print("Entrada invalida.")
            print_help()


if __name__ == "__main__":
    main()
