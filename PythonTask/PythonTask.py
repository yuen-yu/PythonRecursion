import codecs
import pyodbc

class Item:
    def __init__(self, symbol, portx, porty, nodex, nodey):
        self.symbol = symbol
        self.portx = portx
        self.porty = porty             
        self.nodex = nodex
        self.nodey = nodey
   
t_sql = [
            "DROP TABLE IF EXISTS result;",
            "DROP TABLE IF EXISTS resource;",
            "CREATE TABLE result (Symbol NVARCHAR(10) NOT NULL, Portx INTEGER, Porty INTEGER, Nodex INTEGER, Nodey INTEGER);",
            "CREATE TABLE resource (Symbol NVARCHAR(10) NOT NULL, x INTEGER NOT NULL, y INTEGER NOT NULL);"
        ]

data = [
            ("═", -1,  0),
            ("═",  1,  0),            
            ("║",  0, -1),
            ("║",  0,  1),            
            ("╔",  0, -1),
            ("╔",  1,  0),            
            ("╗", -1,  0),
            ("╗",  0, -1),            
            ("╚",  1,  0),
            ("╚",  0,  1),            
            ("╝", -1,  0),
            ("╝",  0,  1),            
            ("╠",  0,  1),
            ("╠",  0, -1),
            ("╠",  1,  0),
            ("╣", -1,  0),  
            ("╣",  0,  1),  
            ("╣",  0, -1), 
            ("╦", -1,  0),          
            ("╦",  1,  0), 
            ("╦",  0, -1),
            ("╩", -1,  0),         
            ("╩",  1,  0),
            ("╩",  0,  1) 
        ]

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};Server=(local)\SQLEXPRESS;Database=test;Trusted_Connection=yes')


def createDBs(conn, sqls):
    try:
        cursor = conn.cursor()                 
        for s in sqls:
            cursor.execute(s)     
        conn.commit()
    except pyodbc.Error as e:
        print(e)


def loadResource(conn, data):
    sql = "INSERT INTO resource VALUES (?, ?, ?)"
    try:
        cursor = conn.cursor()
        cursor.executemany(sql, data)
        conn.commit()
    except pyodbc.Error as e:
        print(e)


def getResource(conn, symbol):
    sql = "SELECT x, y FROM resource WHERE Symbol = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (symbol,))
        rows = cursor.fetchall()
        conn.commit()
        return rows
    except pyodbc.Error as e:
        print(e)


def loadResult(conn, inputs):    
    sqls = []
    obj = inputs[0]
    try:
        i1 = int(inputs[1])
        i2 = int(inputs[2])
    except ValueError:
        print("location " + obj + " not integer: " + inputs[1] + " " + inputs[2])
        exit()
   
    if ((obj == "*") | (obj.isalpha() == True)): 
         sql = f"INSERT INTO result (Symbol, Nodex, Nodey) VALUES ('{obj}', {i1}, {i2});"
         sqls.append(sql)
    else:
         rows = getResource(conn, obj)
         if rows:
             for r in rows:
                Px = i1 + r[0]
                Py = i2 + r[1]
                Nx = i1
                Ny = i2
                sql = f"INSERT INTO result (Symbol, Portx, Porty, Nodex, Nodey) VALUES (N'{obj}', {Px}, {Py}, {Nx}, {Ny});"
                sqls.append(sql)

    if sqls:
        try:
            cursor = conn.cursor()
            for s in sqls:
                cursor.execute(s)           
            conn.commit()
        except pyodbc.Error as e:
            print(e)


def findSource():
    source = "*"
    sql = "SELECT Nodex, Nodey FROM result WHERE Symbol= ?"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (source,))
        row = cursor.fetchone()
        conn.commit()
        return row
    except pyodbc.Error as e:
        print(e)


def findFirstPortAndNode(x,y):

    sql = "SELECT * FROM result WHERE Portx = ? and Porty = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (x,y,))
        row = cursor.fetchone()
        conn.commit()
        return row
    except pyodbc.Error as e:
        print(e)


def findOtherPortsSameNode(portx, porty, nodex, nodey):
    sql = "SELECT * FROM result WHERE Nodex = ? AND Nodey = ? AND NOT (Portx = ? AND Porty = ?)"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (nodex, nodey, portx, porty,))
        rows = cursor.fetchall()
        conn.commit()
        return rows
    except pyodbc.Error as e:
        print(e)


def matchNodeWithPort(portx, porty, nodex, nodey):
    sql  = "SELECT * FROM result WHERE Nodex = ? AND Nodey = ? AND Portx = ? AND Porty = ?"
    sql2 = "SELECT * FROM result WHERE Nodex = ? AND Nodey = ?" 
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (portx,porty,nodex,nodey,))
        row = cursor.fetchone()
        if row == None:
            cursor.execute(sql2, (portx,porty,))
            row = cursor.fetchone()
        conn.commit()
        return row
    except pyodbc.Error as e:
        print(e)
        

def main():
    createDBs(conn, t_sql)
    loadResource(conn, data)
    filename = input("Please enter a file name (include file path): ")
    try:
        # Attempt to open the file
        f = codecs.open(filename, "rb", encoding='utf-8-sig')
        lines = f.readlines()
        for line in lines:
            line = line.rstrip('\r\n')
            inputs = line.split(" ")
            loadResult(conn, inputs)
        f.close()
    except FileNotFoundError:
        print("The file " + filename + " does not exist.")

 



    Nodes=[]
    finalList=[]

    
    rowSource = findSource()
    if rowSource:
        sourceX = rowSource[0]
        sourceY = rowSource[1]
        row1 = findFirstPortAndNode(sourceX,sourceY)
        Nodes.append(Item(row1[0], row1[1], row1[2], row1[3], row1[4]))        
        for n in Nodes:
            if ((n.symbol).isalpha() == True):
                finalList.append(n.symbol)
                print("find sink " + n.symbol)
            else:
                Ports = findOtherPortsSameNode(n.portx, n.porty, n.nodex, n.nodey)
                for p in Ports:
                    newNode = matchNodeWithPort(p[1],p[2],p[3],p[4])
                    if newNode:
                        Nodes.append(Item(newNode[0], newNode[1], newNode[2], newNode[3], newNode[4]))
    else:
        print("No source in the file.")    
    print("Finallist = " + "".join(finalList))

if __name__ == "__main__":
    main()