
import customtkinter as ctk
import functions
from functions import *
import psycopg2
import webbrowser

if __name__ == "__main__":

    connection, cursor = open_connection_DB()

    #load_gz_recipe_to_table(connection,cursor)
    #insert_ingredients(connection, cursor)

    # Imposta la modalità di aspetto e il tema predefinito
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    # Crea la finestra principale
    window = ctk.CTk()
    window.title("Choose your recipe")

    # Crea il frame header
    frame_header = ctk.CTkFrame(window, width=600, height=100, corner_radius=20, fg_color="#1E3A8A")  # blu scuro
    frame_header.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    # Crea il frame body
    frame_body = ctk.CTkFrame(window, width=600, height=250, corner_radius=20, fg_color="#BFDBFE")  # blu chiaro
    frame_body.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

    # Crea il frame footer
    frame_footer = ctk.CTkFrame(window, width=600, height=100, corner_radius=20, fg_color="#93C5FD")  # azzurro
    frame_footer.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

    # Configura il peso delle righe della finestra principale
    window.grid_rowconfigure(0, weight=1)
    window.grid_rowconfigure(1, weight=3)
    window.grid_rowconfigure(2, weight=1)

    # Configura il peso delle righe e colonne del frame_header
    frame_header.grid_rowconfigure(0, weight=1)
    frame_header.grid_columnconfigure(0, weight=1)

    # Configura il peso delle righe e colonne del frame_body
    frame_body.grid_rowconfigure(0, weight=1)
    frame_body.grid_columnconfigure(0, weight=1)
    frame_body.grid_columnconfigure(1, weight=1)

    # Configura il peso delle righe e colonne del frame_footer
    frame_footer.grid_rowconfigure(0, weight=1)
    frame_footer.grid_columnconfigure(0, weight=1)
    frame_footer.grid_columnconfigure(1, weight=1)
    frame_footer.grid_columnconfigure(2, weight=1)

    # Aggiungi il label nella parte superiore del frame_header
    label_header = ctk.CTkLabel(frame_header, text="From here you can choose which recipe to make", font=("Bold", 24), text_color="white")
    label_header.grid(row=0, column=0, columnspan=3, padx=10, pady=20, sticky="nsew")

    # Aggiungi il label nel frame_body per i suggerimenti sugli ingredienti
    label_body = ctk.CTkLabel(frame_body, text="Choose the ingredients", font=("Bold", 20), text_color="#1E3A8A")  # blu scuro
    label_body.grid(row=0, column=0, columnspan=2, padx=10, pady=20, sticky="nsew")

    # Crea un frame scorrevole all'interno del frame_body
    scrollable_frame = ctk.CTkScrollableFrame(frame_body, width=200, height=150, fg_color="#ffffff")
    scrollable_frame.grid(row=1, column=1, padx=10, pady=20, sticky="nsew")

    # Aggiungi gli ingredienti come etichette all'interno dello scrollable frame
    #ingredients = ["Tomato", "Cheese", "Basil", "Olive Oil", "Garlic"]
    ingredients = []

    ingredient_labels = []  # Lista per tenere traccia delle etichette degli ingredienti

    for ingredient in ingredients:
        ingredient_label = ctk.CTkLabel(scrollable_frame, text=ingredient, text_color="#1E3A8A")
        ingredient_label.pack(anchor="w", pady=5)
        ingredient_labels.append(ingredient_label)

    # Aggiungi un campo di inserimento per aggiungere nuovi ingredienti
    ingredient_entry = ctk.CTkEntry(frame_body, placeholder_text="Enter new ingredient", fg_color="#ffffff", text_color="#1E3A8A", border_width=1, border_color="#1E3A8A")
    ingredient_entry.grid(row=1, column=0, padx=10, pady=10, sticky="w")

    # Funzione per aggiungere l'ingrediente
    def add_ingredient():
        new_ingredient = ingredient_entry.get()
        if new_ingredient:
            ingredient_label = ctk.CTkLabel(scrollable_frame, text=new_ingredient, fg_color="#93C5FD", corner_radius=10, text_color="white")  # azzurro
            ingredient_label.pack(anchor="center", pady=5)
            ingredient_labels.append(ingredient_label)  # Aggiungi l'etichetta alla lista
            ingredient_entry.delete(0, "end")  # Pulisce il campo di inserimento

    # Funzione per cancellare tutti gli ingredienti
    def clear_ingredients():
        for label in ingredient_labels:
            label.destroy()  # Rimuovi ogni etichetta
        ingredient_labels.clear()  # Pulisci la lista di etichette

    # Aggiungi un bottone per inserire l'ingrediente
    add_button = ctk.CTkButton(frame_body, text="Add Ingredient", command=add_ingredient, fg_color="#1E3A8A", text_color="white", font=("Arial", 16))
    add_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    # Aggiungi un bottone per cancellare tutti gli ingredienti
    clear_button = ctk.CTkButton(frame_body, text="Clear Ingredients", command=clear_ingredients, fg_color="#EF4444", text_color="white", font=("Arial", 16, "bold"))
    clear_button.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

    def call_search_recipe():
        list = [label.cget("text") for label in ingredient_labels]
        data = search_recipe(list, cursor)
        display_recipes(data)

    recipe_scrollable_frame = ctk.CTkScrollableFrame(frame_footer)
    recipe_scrollable_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    # Funzione per visualizzare le ricette nella lista scorrevole
    import webbrowser

    def display_recipes(recipes):
        # Pulisce i risultati precedenti nel frame scrollabile
        for widget in frame_footer.winfo_children():
            widget.destroy()

        # Verifica se ci sono ricette da visualizzare
        if recipes.empty:
            no_results_label = ctk.CTkLabel(frame_footer, text="No recipes found", font=("Arial", 16, "bold"), text_color="#EF4444")
            no_results_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
            return

        # Crea un frame scorrevole per le ricette nel frame_footer
        scrollable_recipe_frame = ctk.CTkScrollableFrame(frame_footer)
        scrollable_recipe_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=20, sticky="nsew")

        # Itera su ogni ricetta nel DataFrame
        for index, recipe in recipes.iterrows():
            # Creazione di un frame elegante per ogni ricetta con un bordo e un po' di padding
            recipe_frame = ctk.CTkFrame(scrollable_recipe_frame, height=120, corner_radius=10, fg_color="#BFDBFE", border_width=2, border_color="#1E3A8A")  # blu chiaro con bordi blu scuro
            recipe_frame.grid(row=index, column=0, padx=10, pady=10, sticky="ew")

            # Nome della ricetta - più grande, grassetto e colore distintivo
            label_name = ctk.CTkLabel(recipe_frame, text=f"Recipe: {recipe['rec_name']}", anchor="w", font=("Arial", 16, "bold"), text_color="#1E3A8A")
            label_name.grid(row=0, column=0, padx=10, pady=5, sticky="w")

            # Categoria della ricetta - meno prominente, ma comunque visibile
            label_category = ctk.CTkLabel(recipe_frame, text=f"Category: {recipe['rec_category']}", anchor="w", font=("Arial", 12), text_color="#1E3A8A")
            label_category.grid(row=1, column=0, padx=10, pady=5, sticky="w")

            # Ingredienti della ricetta - con un po' di margine e testo più piccolo
            if isinstance(recipe['rec_ingredients'], list):
                ingredients_text = ", ".join([f"{item[0]} - {item[1]}" for item in recipe['rec_ingredients']])
            else:
                ingredients_text = str(recipe['rec_ingredients'])

            label_ingredients = ctk.CTkLabel(recipe_frame, text=f"Ingredients: {ingredients_text}", anchor="w", wraplength=300, font=("Arial", 11), text_color="#1E3A8A")
            label_ingredients.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="w")

            # Link della ricetta (se disponibile) - con il colore blu per evidenziare il link
            if recipe['rec_link']:
                # Aggiungiamo un evento che aprirà il browser quando l'utente clicca sul link
                def open_link(event, url=recipe['rec_link']):
                    webbrowser.open(url)

                label_link = ctk.CTkLabel(recipe_frame, text=f"Link: {recipe['rec_link']}", anchor="w", font=("Arial", 10, "italic"), text_color="#1E3A8A")
                label_link.grid(row=3, column=0, padx=10, pady=5, sticky="w")

                # Bind dell'evento per aprire il link al clic
                label_link.bind("<Button-1>", open_link)

            # Separatore visivo tra le ricette
            separator = ctk.CTkFrame(scrollable_recipe_frame, height=2, corner_radius=5, fg_color="grey")
            separator.grid(row=index + 1, column=0, padx=10, pady=5, sticky="ew")



    # Aggiungi il bottone "Cerca Ricetta" nel frame_body sotto i bottoni esistenti
    search_button = ctk.CTkButton(frame_body, text="Search Recipe", command=lambda: call_search_recipe(), fg_color="#1E3A8A", text_color="white", font=("Arial", 16, "bold"))
    search_button.grid(row=3, column=0, columnspan=2, padx=10, pady=20, sticky="nsew")

    # Avvia l'interfaccia grafica
    window.mainloop()

    close_connection_DB(connection, cursor)
