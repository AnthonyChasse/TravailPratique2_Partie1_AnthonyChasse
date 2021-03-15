import mysql.connector
import os


def verification_form_produits(state, request):
    if not len(request.form['code'].strip()) == 8:
        state["valid"] = False
        state["message"] = f"Il faut que le code ai 8 caractères"
    if not 50 > len(request.form['nom'].strip()) > 3:
        state["valid"] = False
        state["message"] = f"{state['message']} - Il faut que le nom soit entre 3 et 50 caractères"
    found = False
    for lignes in lignes_produits_page_accueil():
        if request.form['ligne'].strip() == lignes[0]:
            found = True
    if not found:
        state["valid"] = False
        state["message"] = f"{state['message']} - La ligne n'existe pas"
    if not request.form['echelle'].strip() in ['1:10', '1:12', '1:18', '1:72', '1:24', '1:32', '1:50', '1:700']:
        state["valid"] = False
        state["message"] = f"{state['message']} - L'échelle est invalide (10, 12, 18, 24, 32, 50, 72, 700)"
    if not 150 > len(request.form['vendeur'].strip()) > 3:
        state["valid"] = False
        state["message"] = f"{state['message']} - Il faut que le vendeur soit entre 3 et 150 caractères"
    if not 500 > len(request.form['desc'].strip()) > 3:
        state["valid"] = False
        state["message"] = f"{state['message']} - Il faut que la description soit entre 500 et 3 caractères"
    if not float(request.form['buy_price'].strip()) > 0:
        state["valid"] = False
        state["message"] = f"{state['message']} - Le prix d'achat doit être au dessus de 0"
    if not float(request.form['msrp'].strip()) > 0:
        state["valid"] = False
        state["message"] = f"{state['message']} - Le prix de vente doit être au dessus de 0"
    if not int(request.form['quant'].strip()) >= 0:
        state["valid"] = False
        state["message"] = f"{state['message']} - La quantité en stock doit être 0 ou plus"
    return state


def verification_form_lignes(state, request):
    if not 50 > len(request.form['nom']) > 3:
        state['valid'] = False
        state['message'] = "Le nom est invalide"
    if not 1000 > len(request.form['desc']) > 3:
        state['valid'] = False
        state['message'] = f"{state['message']} - La description est invalide"
    return state


def remplacer_image_produit(state, request):
    if state['has_image']:
        os.remove(fr'static/uploads/{state["filename"]}')
    os.rename(fr'static/uploads/{request.files["image"].filename}',
              fr'static/uploads/{state["filename"]}')


def connection_base_donnees():
    connection = mysql.connector.connect(
        host='localhost',
        database='classicmodels',
        user='root',
        password='',
        port='3308')
    return connection


def ajoute_bool_image(records):
    all_obj = []
    for obj in records:
        if os.path.isfile(fr'static/uploads/{obj[0]}.png'):
            obj += (True,)
        else:
            obj += (False,)
        all_obj.append(obj)
    return all_obj


def lignes_produits_page_accueil():
    try:
        connection = connection_base_donnees()
        if connection.is_connected():
            sql_select_query = """select productLine from productLines"""
            cursor = connection.cursor()
            cursor.execute(sql_select_query)
            line_records = cursor.fetchall()
            return ajoute_bool_image(line_records)
    except mysql.connector.Error as e:
        print("Oops y'a une erreur : ", e)
    finally:
        if connection.is_connected():
            connection.close()


def produits_page_accueil():
    try:
        connection = connection_base_donnees()
        if connection.is_connected():
            sql_select_query = """SELECT productName, MSRP from products order by quantityInStock desc limit 5"""
            cursor = connection.cursor()
            cursor.execute(sql_select_query)
            records = cursor.fetchall()
            return ajoute_bool_image(records)
    except mysql.connector.Error as e:
        print("Oops y'a une erreur : ", e)
    finally:
        if connection.is_connected():
            connection.close()


def ligne_detail(ligne):
    state = {
        "valid": True,
        "has_image": False,
        "message": "",
        "ligne": {},
    }
    try:
        connection = connection_base_donnees()
        if connection.is_connected():
            sql_select_query = """SELECT * from productLines where productLine like %s"""
            cursor = connection.cursor(dictionary=True)
            params = ('%{}%'.format(ligne),)
            cursor.execute(sql_select_query, params)
            records = cursor.fetchall()
            cursor.close()
            if len(records) != 1:
                state["valid"] = False
                state["message"] = f"Aucune ligne ne correspont à {ligne}"
            else:
                state["valid"] = True
                if os.path.isfile(fr'static/uploads/{ligne}.png'):
                    state["has_image"] = True
                state["ligne"] = records[0]
    except mysql.connector.Error as e:
        state["message"] = f"Erreur SQL {e}"
    finally:
        connection.close()
        return state


def produit_detail(product_name):
    state = {
        "valid": True,
        "has_image": False,
        "message": "",
        "produit": {},
    }
    try:
        connection = connection_base_donnees()
        if connection.is_connected():
            sql_select_query = """SELECT * from products where productName like %s"""
            cursor = connection.cursor(dictionary=True)
            params = ('%{}%'.format(product_name),)
            cursor.execute(sql_select_query, params)
            records = cursor.fetchall()
            cursor.close()
            if len(records) != 1:
                state["valid"] = False
                state["message"] = f"Aucun produit ne correspont à {product_name}"
            else:
                state["valid"] = True
                if os.path.isfile(fr'static/uploads/{product_name}.png'):
                    state["has_image"] = True
                state["produit"] = records[0]
    except mysql.connector.Error as e:
        state["message"] = f"Erreur SQL {e}"
    finally:
        connection.close()
        return state


def recherche_produits_par_ligne(ligne):
    try:
        connection = connection_base_donnees()
        if connection.is_connected():
            sql_select_query = """SELECT productName from products where productLine like %s"""
            cursor = connection.cursor()
            params = ('%{}%'.format(ligne),)
            cursor.execute(sql_select_query, params)
            records = cursor.fetchall()
            return records
    except mysql.connector.Error as e:
        print("Oops y'a une erreur : ", e)
    finally:
        if connection.is_connected():
            connection.close()


def recherche_produit(product_name, page=1):
    try:
        connection = connection_base_donnees()
        if connection.is_connected():
            offset = (page - 1) * 10
            sql_select_query = """SELECT productName, MSRP from products where productName 
            like %s or productDescription like %s limit %s,10"""
            cursor = connection.cursor()
            params = ('%{}%'.format(product_name), '%{}%'.format(product_name), offset)
            cursor.execute(sql_select_query, params)
            records = cursor.fetchall()
            return ajoute_bool_image(records)
    except mysql.connector.Error as e:
        print("Oops y'a une erreur : ", e)
    finally:
        if connection.is_connected():
            connection.close()


def modifier_produit(request):
    state = {
        "valid": True,
        "has_image": produit_detail(request.form['nom'])['has_image'],
        "filename": "",
        "message": "",
        "produit": {}
    }
    state = verification_form_produits(state, request)
    if not state['valid']:
        return state
    try:
        connection = connection_base_donnees()
        if connection.is_connected():
            sql_select_query = """update products set productCode = %s, productName = %s,
             productLine = %s, productScale = %s, productVendor = %s, productDescription = %s,
             quantityInStock = %s, buyPrice = %s, MSRP = %s where productName = %s"""
            cursor = connection.cursor(dictionary=True)
            params = (request.form['code'].strip(), request.form['nom'].strip(), request.form['ligne'].strip(),
                      request.form['echelle'].strip(), request.form['vendeur'].strip(), request.form['desc'].strip(),
                      request.form['quant'], request.form['buy_price'], request.form['msrp'], request.form['p_nom'])
            cursor.execute(sql_select_query, params)
            connection.commit()

    except mysql.connector.Error as e:
        state['valid'] = False
        state['message'] = f"Erreur SQL {e}"
    finally:
        if connection.is_connected():
            connection.close()
            state["produit"] = produit_detail(request.form['nom'])['produit']
            if request.files['image']:
                state["filename"] = f'{state["produit"]["productName"]}.png'
                remplacer_image_produit(state, request)
                state["has_image"] = True
            return state


def create_produit(request):
    state = {
        "valid": True,
        "has_image": False,
        "filename": "",
        "message": "",
        "produit": {},
    }
    state = verification_form_produits(state, request)
    if not request.files['image']:
        state['valid'] = False
        state["message"] = f"{state['message']} - La photo est invalide"
    if not state['valid']:
        return state
    try:
        connection = connection_base_donnees()
        if connection.is_connected():
            sql_select_query = """insert into products values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor = connection.cursor(dictionary=True)
            params = (request.form['code'].strip(), request.form['nom'].strip(), request.form['ligne'].strip(),
                      request.form['echelle'].strip(), request.form['vendeur'].strip(),
                      request.form['desc'].strip(),
                      request.form['quant'], request.form['buy_price'], request.form['msrp'])
            cursor.execute(sql_select_query, params)
            connection.commit()
    except mysql.connector.Error as e:
        state['valid'] = False
        state['message'] = f"Erreur SQL {e}"
    finally:
        if connection.is_connected():
            connection.close()
            state["produit"] = produit_detail(request.form['nom'])['produit']
            state["filename"] = f'{state["produit"]["productName"]}.png'
            remplacer_image_produit(state, request)
            state["has_image"] = True
            return state


def supprimer_produit(request):
    try:
        connection = connection_base_donnees()
        if connection.is_connected():
            sql_select_query = """delete from products where productName = %s"""
            cursor = connection.cursor(dictionary=True)
            params = (request.form['nom'].strip(),)
            cursor.execute(sql_select_query, params)
            connection.commit()

    except mysql.connector.Error as e:
        print(f"Erreur SQL {e}")
    finally:
        if connection.is_connected():
            connection.close()
            if request.files['image']:
                filename = f'{request.form["nom"]}.png'
                os.remove(fr"static/uploads/{filename}")


def modifier_ligne(request):
    state = {
        "valid": True,
        "message": "",
        "filename": "",
        "has_image": ligne_detail(request.form['nom'])['has_image'],
        "ligne": {}
    }
    state = verification_form_lignes(state, request)
    if not state["valid"]:
        return state
    try:
        connection = connection_base_donnees()
        if connection.is_connected():
            sql_select_query = """update productLines set productLine = %s, textDescription = %s
             where productLine = %s"""
            cursor = connection.cursor(dictionary=True)
            params = (request.form['nom'].strip(), request.form['desc'].strip(), request.form['p_nom'])
            cursor.execute(sql_select_query, params)
            connection.commit()

    except mysql.connector.Error as e:
        state['valid'] = False
        state['message'] = f"Erreur SQL {e}"
    finally:
        if connection.is_connected():
            connection.close()
            state['ligne'] = ligne_detail(request.form['nom'])['ligne']
            state["filename"] = f'{state["ligne"]["productLine"]}.png'
            if state['has_image']:
                os.remove(fr'static/uploads/{state["filename"]}')
            os.rename(fr'static/uploads/{request.files["image"].filename}',
                      fr'static/uploads/{state["filename"]}')
            state["has_image"] = True
            return state


def create_ligne(request):
    state = {
        "valid": True,
        "message": "",
        "filename": "",
        "has_image": True,
        "ligne": {}
    }
    state = verification_form_lignes(state, request)
    if not request.files['image']:
        state['valid'] = False
        state["message"] = f"{state['message']} - La photo est invalide"
    if not state["valid"]:
        return state
    try:
        connection = connection_base_donnees()
        if connection.is_connected():
            sql_select_query = """insert into productLines(productLine, textDescription) values(%s, %s)"""
            cursor = connection.cursor(dictionary=True)
            params = (request.form['nom'].strip(), request.form['desc'].strip())
            cursor.execute(sql_select_query, params)
            connection.commit()

    except mysql.connector.Error as e:
        state['valid'] = False
        state['message'] = f"Erreur SQL {e}"
    finally:
        if connection.is_connected():
            connection.close()
            state['ligne'] = ligne_detail(request.form['nom'])['ligne']
            state["filename"] = f'{state["ligne"]["productLine"]}.png'
            os.rename(fr'static/uploads/{request.files["image"].filename}',
                      fr'static/uploads/{state["filename"]}')
            state["has_image"] = True
            return state
