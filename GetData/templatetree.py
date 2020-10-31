import json
import os
import numpy as np
import pandas as pd
from django.db import connection
from django.db import connections
from django_pandas.io import read_frame
from .models import (Testtempfolderinfo, Testtempfoldertree)

cacheFilePath = "C:\\data\\json.txt"


def get_remaing_nodes():
    with connection.cursor() as cursor:
        var = "SELECT ParentID, ChildID FROM TestTempFolderTree LEFT JOIN TestTempFolderInfo TTFI WITH(NOLOCK) ON TTFI.FolderID = TestTempFolderTree.ChildID AND TTFI.ProjectID = 1072 \
              WHERE TestTempFolderTree.ProjectID = 1072 AND ParentID NOT IN (SELECT FolderID FROM TestTempFolderInfo WITH(NOLOCK) WHERE FolderTitle = 'Nvidia Root Folder' \
              AND AncestorIDPath LIKE '%\\46\\%' AND ProjectID = 1072) AND ParentID != 0\
              AND AncestorIDPath LIKE '%\\46\\%'"
        cursor.execute(var)
        row = cursor.fetchall()
        df = pd.DataFrame(row)
        df.columns = ['parentid', 'childid']
        return df


def get_folders_with_wbt_templates():
    with connection.cursor() as cursor:
        var = """SELECT AncestorIDPath ,FolderId, (SELECT COUNT(*) FROM [TestTempGeneralInfo] [TC] WITH(NOLOCK) 
               WHERE [TC].[ProjectID] = [TTFI].[ProjectID] 
              AND [TC].[TestTempFolderID] = [TTFI].[FolderID] AND TC.FieldINt10 = 1) [TemplateCount] 
              FROM TestTempFolderInfo [TTFI] WITH(NOLOCK) WHERE ProjectID = '1072' AND ((FolderStatusID != '2' AND FolderStatusID != '3') OR FolderStatusID IS NULL) AND FolderTitle IS NOT NULL \
              AND AncestorIDPath IS NOT NULL ORDER BY FolderTitle"""
        cursor.execute(var)
        row = cursor.fetchall()
        df = pd.DataFrame(row)
        df.columns = ['AncestorIDPath', 'FolderId', 'TemplateCount']
        df = df.loc[df['TemplateCount'] > 0]
        new = df.AncestorIDPath.str.split('\\', n=3, expand=True)
        df['ParentID'] = new[2]
        df['ParentID'].replace('', np.nan, inplace=True)
        df.dropna(subset=['ParentID'], inplace=True)
        return df


def get_nodes():
    with connection.cursor() as cursor:
        var = " SELECT FolderID, FolderTitle FROM TestTempFolderInfo  WITH(NOLOCK) WHERE ProjectID = 1072 AND AncestorIDPath LIKE '%\\46\\%' "
        cursor.execute(var)
        row = cursor.fetchall()
        df = pd.DataFrame(row)

        df.columns = ['folderid', 'foldertitle']
        return df


def load_data():

    dict_folder_titles = Testtempfolderinfo.objects.filter(
        projectid=1072, ancestoridpath__icontains='\\46\\').values('folderid', 'foldertitle')
    dict_folder_titlesdf = read_frame(dict_folder_titles)

    dict_wbt_folders = get_folders_with_wbt_templates()
    listroot = dict_wbt_folders.ParentID.unique()

    get_root_nodes = Testtempfoldertree.objects.filter(
        projectid=1072, parentid=46).values('parentid', 'childid')
    get_root_nodesdf = read_frame(get_root_nodes)
    get_root_nodesdf[get_root_nodesdf['childid'].isin(listroot)]
   # print(get_root_nodesdf)

    dict_wbt_folders_explode = pd.concat([pd.Series(row['AncestorIDPath'], row['AncestorIDPath'].split('\\')[1:])
                                          for _, row in dict_wbt_folders.iterrows()]).reset_index()
    dict_wbt_folders_explode.columns = ['AncestorIDPath_Key', 'AncestorIDPath']
    dict_wbt_folders_explode['AncestorIDPath_Key'].replace(
        '', np.nan, inplace=True)
    dict_wbt_folders_explode.dropna(
        subset=['AncestorIDPath_Key'], inplace=True)
    dict_wbt_folders_new = pd.merge(
        dict_wbt_folders, dict_wbt_folders_explode, how='inner', on=['AncestorIDPath'])
    dict_wbt_folders_new['AncestorIDPath_Key'] = dict_wbt_folders_new['AncestorIDPath_Key'].apply(
        lambda x: "{}{}{}".format('\\', x, '\\'))
    # print(dict_wbt_folders_new)

    remaining_nodes_df = get_remaing_nodes()
    remaining_nodes_df['childid_new'] = remaining_nodes_df['childid'].apply(
        lambda x: "{}{}{}".format('\\', x, '\\'))

    # print(Remaining_nodes_df)

    remaining_nodes_df_new = pd.merge(remaining_nodes_df, dict_wbt_folders_new, how='inner', left_on=[
                                      'childid_new'], right_on=['AncestorIDPath_Key'])

    parent_df = remaining_nodes_df_new.drop(
        ['AncestorIDPath', 'FolderId', 'TemplateCount', 'ParentID', 'AncestorIDPath_Key', 'childid_new'], 1)
   # print(parent_df)
    get_root_nodesdf = get_root_nodesdf.append(parent_df, ignore_index=True)

    full_nodes_df = pd.merge(get_root_nodesdf, dict_folder_titlesdf, left_on='childid',
                             right_on='folderid', how='left').drop('childid', axis=1)
    print(full_nodes_df)
    jsondata = full_nodes_df.to_json(orient='records')
    return jsondata


def get_cache_data(flag):
    if os.path.exists(cacheFilePath):
        if flag == 'true':
            f = open(cacheFilePath)
            fread = f.read()
            jsonstring = json.loads(fread)
            print(type(jsonstring))
            jsondata = jsonstring
        else:
            jsondata = load_data()
            with open(cacheFilePath, 'w') as f:
                json.dump(jsondata, f, ensure_ascii=False)
    else:
        jsondata = load_data()
        with open(cacheFilePath, 'w') as f:
            json.dump(jsondata, f, ensure_ascii=False)

    return jsondata


def main():
    get_cache_data(flag=True)


if __name__ == "__main__":
    print("hello")
    main()
