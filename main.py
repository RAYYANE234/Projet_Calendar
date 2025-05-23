import import_edt
import mistral

def main():
    print(" Exécution du script 1 : import de l'emploi du temps")
    import_edt.main()

    print("\n Exécution du script 2 : mise à jour via Mistral")
    mistral.main()

    print("\n Tous les scripts ont été exécutés.")

if __name__ == "__main__":
    main()
