import cx_Oracle

connection = None
cursor = None
useEmbedding = False

print("1 - Embedding")
print("2 - Linking")
ip = input("Voce quer usar o embedding ou linking: ")
if(ip == 1): 
    useEmbedding = True
    print("Embedding selecionado!")
else:
    useEmbedding = False
    print("Linking selecionado!")

script1P = './script1.txt'
script2P = './script2.txt'

script1 = open(script1P, 'w')
script2 = open(script2P, 'w')

def verifyIfIsTheFirstColumn(addedColumns):
    for addedColumn in addedColumns:
        if(addedColumn == 1):
            return False
    return True


def addTupla(col, val, isId=False):
    if(isId):
        command =  '_id: '
    else:
        command = col['name'] + ': '
    colType = col['type'] 
    if(colType == 'VARCHAR2' or colType == 'CHAR' or colType == 'VARCHAR' or colType == 'DATE'):
        command += '"{value}"'.format(value=val)
    else:
        command += ' {value} '.format(value=val)
    
    return command

def addEmbedding(refTupla, fkTable, fk, tables):
    parans = []
    fkValues = []
    for j in range(len(fk['columns'])):
        for k in range(len(fkTable['columns'])):
            if(fkTable['columns'][k]['name'] == fk['columns'][j]['column'] ):
                if(refTupla[k] == None):
                    return ""
                fkValues.append({'column':fk['columns'][j]['column'], 'value':refTupla[k], 'position':fk['columns'][j]['position']})
    pkTable = None
    for table in tables:
        if(table['name'] == fk['relatedTable']['name']):
            pkTable = table
        
    sql = 'SELECT ' + pkTable['columns'][0]['name']
    for i in range(len(pkTable['columns'])):
        if(i > 0):
            sql += ' , ' + pkTable['columns'][i]['name']
    sql += ' FROM ' + pkTable['name']
    sql += ' WHERE '
    for i in range(len(fk['relatedTable']['columns'])):
        if(i > 0):
            sql += ' AND '
        sql+= fk['relatedTable']['columns'][i]['column'] + " = "
        for j in range(len(fkValues)):
            if(fk['relatedTable']['columns'][i]['position'] == fkValues[j]['position']):
                sql+= " :v{n}".format(n=j)
                parans.append(fkValues[j]['value'])
    
    cursor.execute(sql,parans)
    tupla = cursor.fetchone()

    
    addedColumns = [] 
    for i in range(len(pkTable['columns'])):
        addedColumns.append(0)

    command = pkTable['name'] + ': '
    command += '{'
    
    table = pkTable
    #Creating forinKeys
    fkKeys = table['fks'].keys()
    if(len(fkKeys) == 1):
        for fk in table['fks'].keys():
            if(useEmbedding):
                commandTemp = addEmbedding(tupla, table, table['fks'][fk], tables)
                if(verifyIfIsTheFirstColumn(addedColumns) == False and commandTemp != ""):
                    command += ', '
                if(commandTemp != ""):
                    command += commandTemp
                for i in range(len(table['columns'])):
                    for j in range(len(table['columns'])):
                        if(table['columns'][i]['name'] == table['fks'][fk]['columns'][j]['column']):
                            addedColumns[i] = 1
            else:
                commandTemp = addRef(tupla, table, table['fks'][fk])
                if(verifyIfIsTheFirstColumn(addedColumns) == False and commandTemp != ""):
                    command += ', '
                if(commandTemp != ""):
                    command += commandTemp
                for i in range(len(table['columns'])):
                    for j in range(len(table['fks'][fk]['columns'])):
                        if(table['columns'][i]['name'] == table['fks'][fk]['columns'][j]['column']):
                            addedColumns[i] = 1

    elif(len(fkKeys) > 1):
        for fk in table['fks'].keys():
            pass
    #Creating r


    for i in range(len(table['columns'])):
        isTheFistColumn = verifyIfIsTheFirstColumn(addedColumns)
        if (addedColumns[i] == 0):
            if(isTheFistColumn == False and tupla[i] != None):
                command += ', '
            if(tupla[i] != None):
                command += addTupla(table['columns'][i], tupla[i])
            addedColumns[i] = 1

    for relatedTable in tables:
        for key in relatedTable['fks'].keys():
            if(relatedTable['fks'][key]['relatedTable'] == table['name'] and relatedTable['MN']):
                addRefsMN(tupla, table, relatedTable, relatedTable['fks'][key])


    command += '}'
    return command


def addRef(refTupla, fkTable, fk):
    fkValues = []
    for j in range(len(fk['columns'])):
        for k in range(len(fkTable['columns'])):
            if(fkTable['columns'][k]['name'] == fk['columns'][j]['column'] ):
                if(refTupla[k] == None):
                    return ""
                fkValues.append({'column':fk['columns'][j]['column'],'type':fkTable['columns'][k]['type'], 'value':refTupla[k], 'position':fk['columns'][j]['position']})
    
    command = fk['relatedTable']['name'] + "_id: "
    if(len(fkValues) > 1):
        command += '{'

        for i in range(len(fk['relatedTable']['columns'])):
            for j in range(len(fkValues)):
                    if(fk['relatedTable']['columns'][i]['position'] == fkValues[j]['position']):
                        command += fk['relatedTable']['columns'][i]['column'] + ": "
                        if(fkValues[j]['type'] == 'VARCHAR2' or fkValues[j]['type'] == 'CHAR' or fkValues[j]['type'] == 'VARCHAR' or fkValues[j]['type'] == 'DATE'):
                            command += '"{value}"'.format(value=fkValues[j]['value'])
                        else:
                            command += ' {value} '.format(value=fkValues[j]['value'])

        
        command += '}'
    else:
        if(fkValues[0]['type'] == 'VARCHAR2' or fkValues[0]['type'] == 'CHAR' or fkValues[0]['type'] == 'VARCHAR' or fkValues[0]['type'] == 'DATE'):
            command += '"{value}"'.format(value=fkValues[0]['value'])
        else:
            command += ' {value} '.format(value=fkValues[j]['value'])

    return command


def addRefMN(fkValues):
    
    
    command = '{'
    first = True
    for i in range(len(fkValues)):
        if first:
            first = False
        else:
            command = ' , '
        command += fkValues[i]['fk_column'] + ": {value}".format(value=fkValues[i]['value']) 

    
    command += '}'
   

    return command

def addRefsMN(refTupla, pkTable, mnTable, fk):
    pkValues = []
    parans = []
    for j in range(len(pkTable['pk'])):
        print(j)
        for k in range(len(pkTable['columns'])):
            if(pkTable['columns'][k]['name'] == pkTable['pk'][j]['column'] ):
                if(refTupla[k] == None):
                    return ""
                pkValues.append({'pk_column':pkTable['pk'][j]['column'], 'value':refTupla[k], 'position':pkTable['pk'][j]['position']})
    print(refTupla)
    print(pkValues)

    # Relacionar pkTable e mnTable
    sql = 'SELECT ' + mnTable['pk'][0]['column']
    for i in range(len(mnTable['pk'])):
        if(i > 0):
            sql += ' , ' + mnTable['pk'][i]['column']
    sql += ' FROM ' + mnTable['name']
    sql += ' WHERE '
    for i in range(len(fk['relatedTable']['columns'])):
        if(i > 0):
            sql += ' AND '
        sql+= fk['columns'][i]['column'] + " = "
        for j in range(len(pkValues)):
            if(fk['columns'][i]['position'] == pkValues[j]['position']):
                sql+= " :v{n}".format(n=j)
                pkValues[j]['fk_column'] = fk['columns'][i]['column']
                parans.append(pkValues[j]['value'])
    
    print(sql)
    print(parans)
    cursor.execute(sql,parans)
    tuplas = cursor.fetchmany()
    command = mnTable['name'] + "_ids: ["

    first = True
    for tupla in tuplas:
        if first:
            first = False
        else:
            command = ' , '
        fkValues = []
        for i in range(len(mnTable['pk'])):
            fkValues.append({'fk_column':mnTable['pk'][i]['column'],'value':tupla[i]})
        command += addRefMN(fkValues)
    
    command += "]"
    return command

def createTableIndex(table):
    pksString = ""
    first = True
    command = ""
    command += 'db.{tableName}.ensureIndex({pk})\n'.format(tableName=table['name'],pk="{"+"_id:1"+"}")

    if(len(table['unique'].keys()) > 0):
        print("\n\n")
        print(table['unique'])
        print("\n\n")
        uniqueString = ""
        first = True
        
        for uiniqueKey in table['unique'].keys():
            addedsFks = {}
            for uiniqueCol in table['unique'][uiniqueKey]['columns']:
                fkadd = False
                
                
                for fk in table['fks'].keys():
                    for fkCol in table['fks'][fk]['columns']:
                        if( fkCol['column'] == uiniqueCol['column'] ):
                            addedsFks.setdefault(table['fks'][fk]['relatedTable']['name'], 1) 
                            fkadd = True

                if(fkadd == False):
                    if first:
                        first = False
                    else:
                        uniqueString += ' , '
                    uniqueString += uiniqueCol['column'] + ": 1"
        
        for tableName in addedsFks.keys():
            if first:
                first = False
            else:
                uniqueString += ' , '
            uniqueString += tableName + "_id: 1"

        command += 'db.{tableName}.ensureIndex({unique})\n'.format(tableName=table['name'],unique="{"+uniqueString+"}")

    
    script2.write(command)

    



print("")
print("Tentando conectar ao banco de dados....")
print("")
try:
    connection = cx_Oracle.connect('M11234328', 'M11234328', cx_Oracle.makedsn("orclgrad2.icmc.usp.br", 1521, service_name="pdb_junior.icmc.usp.br"))
    print(connection) 
    cursor = connection.cursor()
except ValueError:
    print(ValueError)
    print("Nao foi possivel conectar com o banco de dados!")



try:
    sql = ('SELECT table_name FROM user_tables')

    cursor.execute(sql)
    result = cursor.fetchmany()

    # print(result)

    tables = []
    for table in result:
        tableDict = {
            'name':table[0], 
            'columns':[],
            'pk':[],
            'fks':{},
            'unique':{},
            'MN': False,
            }
        
        sql = ('SELECT column_name, data_type, data_length  FROM USER_TAB_COLUMNS WHERE table_name = :tableName')
        cursor.execute(sql,[table[0]])
        result2 = cursor.fetchmany()
        # print(table[0])
        for column in result2:
            columnDict = {
                'name':column[0],
                'type':column[1],
                'size':column[2]
            }
            # print(column[0])

            sql =   ('SELECT cols.constraint_name, cons.constraint_type, cols.position '
                    'FROM all_constraints cons, all_cons_columns cols '
                    'WHERE cols.table_name = :tableName '
                    'AND cols.column_name =:columnName '
                    #'AND cons.constraint_type = :constraintType '
                    'AND cons.constraint_name = cols.constraint_name ')
            cursor.execute(sql,[table[0],column[0]])
            result4 = cursor.fetchmany()
            for constraint in result4:
                if(constraint[1] == "P"):
                    tableDict['pk'].append({'column':column[0],'position':constraint[2]})
                elif(constraint[1] == "R"):
                    tableDict['fks'].setdefault(constraint[0], {'columns':[], 'relatedTable':{'name':"",'columns':[]}})
                    tableDict['fks'][constraint[0]]['columns'].append({'column':column[0],'position':constraint[2]})
                elif(constraint[1] == "U"):
                    tableDict['unique'].setdefault(constraint[0], {'columns':[]})
                    tableDict['unique'][constraint[0]]['columns'].append({'column':column[0]})


            tableDict['columns'].append(columnDict)

        for fk in tableDict['fks'].keys():
            sql =   (   'SELECT c_pk.table_name, colun.COLUMN_NAME, colun.position '
                        'FROM all_constraints c '
                        'JOIN all_constraints c_pk ON c.r_owner = c_pk.owner '
                        'AND c.r_constraint_name = c_pk.constraint_name '
                        'JOIN all_cons_columns colun ON  c_pk.constraint_name = colun.constraint_name '
                        'WHERE c.constraint_name = :constraintName '
                    )
            cursor.execute(sql,[fk])
            result5 = cursor.fetchmany()
            tableDict['fks'][fk]['relatedTable']['name'] = result5[0][0]
            for relation in result5:
                 tableDict['fks'][fk]['relatedTable']['columns'].append({'column':relation[1],'position':relation[2]})
        
        if(len(tableDict['fks'].keys()) > 1):
            tableDict['MN'] = True
            
        tables.append(tableDict)



    for table in tables:
        print(table)
        createTableIndex(table)
        sql = 'SELECT ' + table['columns'][0]['name']
        for i in range(len(table['columns'])):
            if(i > 0):
                sql += ' , ' + table['columns'][i]['name']
        sql += ' FROM ' + table['name']
        # print(sql)

        cursor.execute(sql)
        tuplas = cursor.fetchmany()
        for tupla in tuplas:
            addedColumns = [] 
            for i in range(len(table['columns'])):
                addedColumns.append(0)

            # print(tupla)
            command = 'db.'+table['name']+'.insertOne({'
            if(len(table['pk']) > 0):

                #Creating pk
                if(len(table['pk']) > 1):
                    command += '_id:'
                    command += '{'
                
                    for pk in table['pk']:
                        for i in range(len(table['columns'])):
                            if(table['columns'][i]['name'] == pk['column']):
                                if(verifyIfIsTheFirstColumn(addedColumns) == False):
                                    command += ', '
                                command += addTupla(table['columns'][i], tupla[i])
                                addedColumns[i] = 1
                    
                    command += '}'

                else:
                    # print('teste')
                    for i in range(len(table['columns'])):
                        if(table['columns'][i]['name'] == table['pk'][0]['column']):
                            command += addTupla(table['columns'][i], tupla[i],True)
                            addedColumns[i] = 1
                
            #Creating forinKeys
            fkKeys = table['fks'].keys()
            if(len(fkKeys) == 1):
                for fk in table['fks'].keys():
                    if(useEmbedding):
                        commandTemp = addEmbedding(tupla, table, table['fks'][fk], tables)
                        if(verifyIfIsTheFirstColumn(addedColumns) == False and commandTemp != ""):
                            command += ', '
                        if(commandTemp != ""):
                            command += commandTemp
                        for i in range(len(table['columns'])):
                            for j in range(len(table['columns'])):
                                if(table['columns'][i]['name'] == table['fks'][fk]['columns'][j]['column']):
                                    addedColumns[i] = 1
                    else:
                        commandTemp = addRef(tupla, table, table['fks'][fk])
                        if(verifyIfIsTheFirstColumn(addedColumns) == False and commandTemp != ""):
                            command += ', '
                        if(commandTemp != ""):
                            command += commandTemp
                        for i in range(len(table['columns'])):
                            for j in range(len(table['fks'][fk]['columns'])):
                                if(table['columns'][i]['name'] == table['fks'][fk]['columns'][j]['column']):
                                    addedColumns[i] = 1

            elif(len(fkKeys) > 1):
                for fk in table['fks'].keys():
                    pass
            #Creating r


            for i in range(len(table['columns'])):
                isTheFistColumn = verifyIfIsTheFirstColumn(addedColumns)
                if (addedColumns[i] == 0):
                    if(isTheFistColumn == False and tupla[i] != None):
                        command += ', '
                    if(tupla[i] != None):
                        command += addTupla(table['columns'][i], tupla[i])
                    addedColumns[i] = 1

            for relatedTable in tables:
                for key in relatedTable['fks'].keys():
                    if(relatedTable['fks'][key]['relatedTable']['name'] == table['name'] and relatedTable['MN']):
                        # command += addRefsMN(tupla, table, relatedTable, relatedTable['fks'][key])
                        pass


            command += '})'

            script1.write(command + '\n')
   
except ValueError:
    print(ValueError)