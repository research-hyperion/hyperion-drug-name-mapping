import os

import pandas as pd
import urllib.request
import numpy as np
from os import path

NOMENCLATOR_EXCEL_FILE: str = "nomenclator medicamente ANMDM.xlsx"
DRUG_NAMES_EN_RO: str = "drug_names_EN_RO.csv"
DRUG_NAMES_MAPPING: str = "drug_names_EN_RO_COMMERCIAL.csv"

NOMENCLATOR_DOWNLOAD_URL: str = "https://nomenclator.anm.ro/files/nomenclator.xlsx"
NOMENCLATOR_NEW_FILE_NAME: str = "nomenclator_new.xlsx"

def get_new_nomenclator_file():
    urllib.request.urlretrieve(NOMENCLATOR_DOWNLOAD_URL,NOMENCLATOR_NEW_FILE_NAME)


def compare_excels_and_update():
    if path.exists(NOMENCLATOR_NEW_FILE_NAME):
        df_old = pd.read_excel(NOMENCLATOR_EXCEL_FILE)
        df_new = pd.read_excel(NOMENCLATOR_NEW_FILE_NAME)
        if not df_old.equals(df_new):

            if not np.array_equal(df_old.values, df_new.values):
                #well we have a difference, update files
                os.remove(NOMENCLATOR_EXCEL_FILE)
                os.rename(NOMENCLATOR_NEW_FILE_NAME,NOMENCLATOR_EXCEL_FILE)
                print("Renamend file...")
                return True
            else:
                os.remove(NOMENCLATOR_NEW_FILE_NAME)
                return False
        else:
            os.remove(NOMENCLATOR_NEW_FILE_NAME)
            return False
    return False

def update_database():
    df_nomenclator = pd.read_excel(NOMENCLATOR_EXCEL_FILE, index_col=0)
    df_drug_names = pd.read_csv(DRUG_NAMES_EN_RO)

    drug_map = []

    for index, row in df_drug_names.iterrows():
        en_drugbank_name = row["EN_DrugBank"]
        ro_drug_name = str(row["RO_ANMDM"])
        if ro_drug_name == "nan":
            continue
        drug_map.append({"en_drug_name": en_drugbank_name, "ro_drug_name": ro_drug_name, "ro_commercial_name": ""})

    for i in range(len(drug_map)):
        entry = drug_map[i]
        comercial_names = "\""
        for index, row in df_nomenclator.iterrows():
            dci = row["DCI"]
            ro_comercial_name = row["Denumire comerciala"]
            if entry["ro_drug_name"] in dci:
                comercial_names += " " + ro_comercial_name
        comercial_names += "\""
        entry["ro_commercial_name"] = comercial_names
        drug_map[i] = entry
        print(f"Writing {entry}...")

    out_df = pd.DataFrame()

    for item in drug_map:
        out_df = out_df.append(item, ignore_index=True)
    out_df.to_csv(DRUG_NAMES_MAPPING)

if __name__ == '__main__':
    print("Donwloading new file...")
    get_new_nomenclator_file()
    if compare_excels_and_update() == True:
        print("Start update database")
        update_database()





