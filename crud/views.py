from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.db import connection
import random,datetime
from django.contrib.auth import login
from django.contrib import messages
from .backend import EmployeeBackend

# Global Variables
R_ID=1

def globalVariable(request):
    with connection.cursor() as cursor:
        cursor.execute('select restaurant_name from restaurant where restaurant_id=%s',(R_ID,))
        name=cursor.fetchone()[0]
    context={'restaurant_name':name.upper}
    return context
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        # Use custom EmployeeBackend for authentication
        backend = EmployeeBackend()
        employee = backend.authenticate(request, email=email, password=password)

        if employee:
            # You can store employee info in session or use Django's login() if user object is needed
            request.session['employee_id'] = employee['employee_id']
            request.session['employee_name'] = employee['employee_name']
            request.session['employee_type'] = employee['employee_type']
            global R_ID
            R_ID=employee['restaurant_id']
            return redirect('view_orders')  # Redirect to a dashboard or any other page
        else:
            messages.error(request, 'Invalid login credentials')

    return render(request, 'login.html')

from django.shortcuts import redirect

def logout_view(request):
    # Clear session
    request.session.flush()
    return redirect('login')  # Redirect to the login page after logging out



# Create your views here.
def view_orders(request):
    query='''select o.order_id,o.table_id,s.employee_name as server_name,k.employee_name as ks_name,
             o.order_type,o.order_date,o.order_time,o.restaurant_id 
             from r_order as o left join employee as s on s.employee_id=o.server_id 
             left join employee as k on k.employee_id=o.kitchen_staff_id 
             where o.restaurant_id=s.restaurant_id and o.restaurant_id=k.restaurant_id and o.restaurant_id=%s  '''



    params=[R_ID]
    o_id=request.GET.get('order_id',None)
    order_type=request.GET.get('order_type',None)
    if o_id:
        query+=' and o.order_id=%s '
        params.append(o_id)
    
    if order_type:
        query+=' and o.order_type=%s ' 
        params.append(order_type)   
        
    sort_order = request.GET.get('sort_order', 'ASC')  # Defaults to ASC

# Validate the sort order
    if sort_order.upper() in ['ASC', 'DESC']:
         query += f' ORDER BY o.order_date {sort_order}, o.order_time {sort_order}'
    else:
        query += ' ORDER BY o.order_date desc, o.order_time desc'



             
    with connection.cursor() as cursor:
        # cursor.execute('select o.order_id,o.table_id,s.employee_name as server_name,k.employee_name as ks_name,o.order_type,o.order_date,o.order_time,o.restaurant_id from r_order as o left join employee as s on s.employee_id=o.server_id left join employee as k on k.employee_id=o.kitchen_staff_id where o.restaurant_id=s.restaurant_id and o.restaurant_id=k.restaurant_id and o.restaurant_id=%s;',(R_ID,))
        cursor.execute(query,params)
        # cursor.execute('select o.order_id,o.table_id,s.employee_name as server_name,k.employee_name as ks_name,o.order_type,o.order_date,o.order_time,o.restaurant_id from r_order as o left join employee as s on s.employee_id=o.server_id left join employee as k on k.employee_id=o.kitchen_staff_id where o.restaurant_id=%s;',(R_ID,))
        row=cursor.fetchall()
    context={'orders':row}    
        
    return render(request,'view_order.html',context)

def view_table(request):
    query='select * from restaurant_table where restaurant_id=%s '
    params=[R_ID]
    status=request.GET.get('table_status',None)
    table_id=request.GET.get('table_id',None)
    if status:
        query+=' and table_status=%s '
        params.append(status)
    if table_id:
        query+=' and table_id=%s'
        params.append(table_id)
    with connection.cursor() as cursor:
        cursor.execute(query,params)
        row=cursor.fetchall()
    context={'tables':row}    
        
    return render(request,'view_table.html',context)


def create_table(request):
    if request.method =='GET':
        return render(request,'create_table.html')
    
    
    else:
     
        t_size=str(request.POST['table_size'])
        t_status=0
        t_r_id=R_ID
        with connection.cursor() as cursor:
           s='restaurant_table'
        #    cursor.execute(f'Select * from {s} where table_id=%s and restaurant_id=%s',(t_id,t_r_id,))
        #    if cursor.fetchone():
        #        return HttpResponse('Table with this id already exists.')
           cursor.execute(f"Insert into {s}(table_size,table_status,restaurant_id) values (%s,%s,%s);",(t_size,t_status,t_r_id))
        #    cursor.execute(f"Update {s} set dept_name= %s where dept_no=%s ;",(d_name,d_id))
           messages.success(request, f"New Table  has  has been successfully added.")
        return redirect('view_tables')
    
def edit_table(request,pk):
    if request.method=='GET':
        with connection.cursor() as cursor:
            cursor.execute("Select * from restaurant_table where table_id=%s and restaurant_id=%s",(pk,R_ID))  
            row=cursor.fetchone()
        context={'table':row}
        return render(request,'edit_table.html',context) 
    
    else: 
        #   d_id=str(request.POST['department_id'])
          t_size=request.POST['table_size']
          t_status=request.POST['table_status']
          with connection.cursor() as cursor:
           s='restaurant_table'
        #    cursor.execute(f"Insert into {s}(dept_no,dept_name) values (%s,%s);",(d_id,d_name))
           cursor.execute(f"Update {s} set table_size= %s , table_status=%s where table_id=%s and restaurant_id=%s ;",(t_size,t_status,pk,R_ID))

           messages.success(request, f"Table ID {pk} has  has been successfully updated.")
           return redirect('view_tables')
       
def delete_table(request,pk):
     with connection.cursor() as cursor:
           s='restaurant_table'
        #    cursor.execute(f"Insert into {s}(dept_no,dept_name) values (%s,%s);",(d_id,d_name))
           cursor.execute(f"Delete from {s} where table_id=%s ;",(pk,))

           messages.success(request, f"Table ID {pk} has  has been successfully deleted.")
           return redirect('view_tables')
       
       
def create_order(request):
    if request.method=='GET':
      with connection.cursor() as cursor:
          cursor.execute('select employee_id, employee_name from employee where restaurant_id=%s and employee_type="SERVER";',(R_ID,))
          serverList=cursor.fetchall()
          
      with connection.cursor() as cursor:
          cursor.execute('select employee_id, employee_name from employee where restaurant_id=%s and employee_type="KITCHEN_STAFF";',(R_ID,))
          kcList=cursor.fetchall()   
          
      with connection.cursor() as cursor:
          cursor.execute('select menu_item_id, menu_name from menu_item natural join menu where restaurant_id=%s;',(R_ID,))
          menuList=cursor.fetchall()
          
      with connection.cursor() as cursor:
          cursor.execute('select table_id from restaurant_table where restaurant_id=%s;',(R_ID,))
          tableList=cursor.fetchall()      
          
      order_type=('DINE_IN','TAKE_OUT')    
          
      context={'servers':serverList,'kcs':kcList,'menus':menuList,'tables':tableList,'order_type':order_type}    
      return render(request,'create_order.html',context)
    else:
        order_id=random.randint(10,100)
        table_id=request.POST['table_id']
        server_id=request.POST['server_id']
        kitchen_id=request.POST['kitchen_staff_id']
        order_type=request.POST['order_type']
        # quantity=request.POST['quantity']
        # menu_item_id=request.POST['menu_item_id']
        order_date=datetime.datetime.now().date() 
        order_time=datetime.datetime.now().time()
        if table_id == 'null':
            with connection.cursor() as cursor:
             cursor.execute('insert into r_order (server_id,kitchen_staff_id,order_type,order_date,order_time,restaurant_id) values(%s,%s,%s,%s,%s,%s)',(server_id,kitchen_id,order_type,order_date,order_time,R_ID))
            with connection.cursor() as cursor:
             cursor.execute('select order_id from r_order where server_id=%s and kitchen_staff_id=%s and order_type=%s and order_date=%s and order_time=%s and restaurant_id=%s;',(server_id,kitchen_id,order_type,order_date,order_time,R_ID))
             order_id=cursor.fetchone()[0]
        else:
         with connection.cursor() as cursor:
            cursor.execute('insert into r_order (table_id,server_id,kitchen_staff_id,order_type,order_date,order_time,restaurant_id)  values(%s,%s,%s,%s,%s,%s,%s)',(table_id,server_id,kitchen_id,order_type,order_date,order_time,R_ID)) 
         with connection.cursor() as cursor:
            cursor.execute('select order_id from r_order where server_id=%s and kitchen_staff_id=%s and order_type=%s and order_date=%s and order_time=%s and restaurant_id=%s;',(server_id,kitchen_id,order_type,order_date,order_time,R_ID))
            order_id=cursor.fetchone()[0]
         with connection.cursor() as cursor:
             cursor.execute('Update restaurant_table set table_status=1 where table_id=%s;,',(table_id,))
            
            
            
        selected_menu_items = request.POST.getlist('menu_items[]')
        
        
        for menu_item_id in selected_menu_items:
            # Get the quantity for the current menu item
            quantity_field_name = f'quantities_{menu_item_id}'
            quantity = request.POST.get(quantity_field_name)

            if quantity:  
                update_inventory(menu_item_id,quantity)
                with connection.cursor() as cursor:
                    cursor.execute('insert into order_menuitem values (%s,%s,%s)',(int(menu_item_id),order_id,int(quantity))) 
        messages.success(request, f"New order {order_id} has  has been successfully created.")
        return redirect('view_orders')   
    
def update_inventory(menu_item_id,quantity):
    with connection.cursor() as cursor:
        cursor.execute('select ingredient_id,quantity from recipe where menu_item_id=%s',(menu_item_id,))
        ingredients=cursor.fetchall()
        
    for i in ingredients:
        with connection.cursor() as cursor:
            total_quantity=int(quantity)*int(i[1])
            cursor.execute('select quantity from inventory where ingredient_id=%s',(i[0],))
            original_quantity=int(cursor.fetchone()[0])
            original_quantity-=total_quantity
            cursor.execute('Update inventory set quantity=%s where ingredient_id=%s',(original_quantity,i[0]))    
         
    
def order_detail(request,pk):
    with connection.cursor() as cursor:
        cursor.execute("select * from r_order where order_id=%s",(pk,))
        order=cursor.fetchone()
    
    with connection.cursor() as cursor:
        cursor.execute('select menu_item_id, quantity,menu_name,price as unit_price, price*quantity as total_price from order_menuitem  natural join menu_item natural join menu  where restaurant_id=%s and order_id=%s;',(R_ID,pk,))    
        details=cursor.fetchall()
    
    total_price=0
    for detail in details:
        total_price+=int(detail[4])
    context={'order':order,'details':details,'total_price':total_price}      
    return render(request,'order_detail.html',context)

def edit_order(request,pk):
    if request.method=='GET':
      with connection.cursor() as cursor:
          cursor.execute('select employee_id, employee_name from employee where restaurant_id= %s and employee_type="SERVER";',(R_ID,))
          serverList=cursor.fetchall()
          
      with connection.cursor() as cursor:
          cursor.execute('select employee_id, employee_name from employee where restaurant_id=%s and employee_type="KITCHEN_STAFF";',(R_ID,))
          kcList=cursor.fetchall()   
          
      with connection.cursor() as cursor:
          cursor.execute('select menu_item_id, menu_name from menu_item natural join menu where restaurant_id=%s;',(R_ID,))
          menuList=cursor.fetchall()
          
      with connection.cursor() as cursor:
          cursor.execute('select table_id from restaurant_table where restaurant_id=%s;',(R_ID,))
          tableList=cursor.fetchall()      
          
      order_type=('DINE_IN','TAKE_OUT')
      
      with connection.cursor() as cursor:
          cursor.execute('''select order_id,table_id,server_id,kitchen_staff_id,order_type,menu_name,mi.menu_item_id,order_type,om.quantity
                            from order_menuitem as om natural join r_order 
                            left join menu_item as mi on om.menu_item_id=mi.menu_item_id 
                            where restaurant_id=%s and order_id=%s;'''
                         ,(R_ID,pk,))
          order=cursor.fetchall()
          print(order)
      
      
      selectedTable=0
      order_id=pk
      table_id=order[0][1]
      server_id=order[0][2]
      kc_ids=order[0][3]
      print(server_id)
      print(serverList)
      selected_order_type=order[0][7]
      context={'servers':serverList,'kcs':kcList,'menus':menuList,'tables':tableList,'order_type':order_type,'order':order,"selectedT":selectedTable,'order_id':order_id,"table_id":table_id,"server_id":server_id,"selected_ot":selected_order_type,'kc_id':kc_ids}    
      return render(request,'edit_order.html',context) 
  
    else:
        order_id=pk
        table_id=request.POST['table_id']
        server_id=request.POST['server_id']
        kc_id=request.POST['kitchen_staff_id']
        order_type=request.POST['order_type']
        with connection.cursor() as cursor:
          cursor.execute('''select order_id,table_id,server_id,kitchen_staff_id,order_type,menu_name,mi.menu_item_id,order_type,om.quantity
                            from order_menuitem as om natural join r_order left join menu_item as mi on om.menu_item_id=mi.menu_item_id  
                            where restaurant_id=%s and order_id=%s;''',(R_ID,pk,))
          order=cursor.fetchall()      
        with connection.cursor() as cursor:
            cursor.execute('Update r_order set table_id=%s, server_id=%s, kitchen_staff_id=%s,order_type=%s where order_id=%s;',(table_id,server_id,kc_id,order_type,order_id))
            
        for mi in order:
            qauntity=request.POST[f'quantities_{mi[6]}']
            with connection.cursor() as cursor:
                cursor.execute('Update order_menuitem set quantity=%s where menu_item_id=%s and order_id=%s;',(qauntity,mi[6],pk)) 
        messages.success(request, f"Order ID {pk}  has been successfully updated.") 
                
        return redirect('view_orders')            

def delete_order(request,pk):
    with connection.cursor() as cursor:
        cursor.execute('Delete from order_menuitem where order_id=%s',(pk,))
        
    with connection.cursor() as cursor:
        cursor.execute('Delete from r_order where order_id=%s',(pk,))  
        
    messages.success(request, f"Order ID {pk}  has been successfully deleted.")
        
    return redirect('view_orders')      

# menu item
def menuitem_list(request):
    query="Select menu_id,menu_item_id,menu_name,price from menu natural join menu_item where restaurant_id=%s "
    params=[R_ID]
    menu_name=request.GET.get('menu_name',None)
    if menu_name:
        query+=" and menu_name=%s"
        params.append(menu_name)
    with connection.cursor() as cursor:
        cursor.execute(query,params)
        menu_items=cursor.fetchall()

   
    context={'menus':menu_items}    
    return render(request,'view_menu_item.html',context)


def create_menu_item(request):
    if request.method=='GET':
         return render(request,'create_menu_item.html')
     
    else:
        
      
        menu_name=request.POST['menu_name']
        price=request.POST['price']
        with connection.cursor() as cursor:
          cursor.execute("Insert into menu_item (menu_name) values(%s)",(menu_name,))
          cursor.execute('select menu_item_id from menu_item where menu_name=%s;',(menu_name,))
          menu_item_id=cursor.fetchone()[0]
          
        with connection.cursor()  as cursor:
            cursor.execute('Insert into menu(menu_item_id,restaurant_id,price) values(%s,%s,%s);',(menu_item_id,R_ID,price))

        messages.success(request, "New Menu Item  has been successfully added.")
          
        return redirect('view_menu_item')



def edit_menu_item(request,pk):
    if request.method=='GET':
         with connection.cursor() as cursor:
          cursor.execute("Select menu_id,menu_item_id,menu_name,price from menu natural join menu_item where restaurant_id=%s and menu_id=%s;",(R_ID,pk))
          menu_item=cursor.fetchone()
         context={'menu':menu_item} 
         return render(request,'edit_menu_item.html',context)
     
    else:
        menu_name=request.POST['menu_name']
        menu_item_id=request.POST['menu_item_id']
        price=request.POST['price']
        with connection.cursor() as cursor:
          cursor.execute("Update menu_item set menu_name=%s where menu_item_id=%s;",(menu_name,menu_item_id))
          
        with connection.cursor() as cursor:
            cursor.execute('Update menu set price=%s where menu_id=%s and restaurant_id=%s;',(price,pk,R_ID))

        messages.success(request, f"Menu Item ID {pk}  has been successfully updated.")
          
        return redirect('view_menu_item') 
    
def delete_menu_item(request,pk):
    with connection.cursor() as cursor:
        cursor.execute('Delete from menu where menu_id=%s;',(pk,))

    messages.success(request, f"Menu ID {pk}  has been successfully deleted.")
    
    return redirect('view_menu_item') 

#employee

def employee_list(request):
    query='select employee_id,employee_name,employee_type from employee where restaurant_id=%s '
    params=[R_ID]
    employee_name=request.GET.get('name',None)
    employee_type=request.GET.get('e_type',None)
    if employee_name:
        query+=" and employee_name=%s"
        params.append(employee_name)
    if employee_type:
        query+=" and employee_type=%s"
        params.append(employee_type)

    print(f'restaurant_id:{R_ID}')
    with connection.cursor() as cursor:
        cursor.execute(query,params)
        emps=cursor.fetchall()
    context={'emps':emps}
    return render(request,'view_employee.html',context)

def create_employee(request):
    if request.method=='GET':
        
         return render(request,'create_employee.html')
     
    else:
      
        employee_name=request.POST['employee_name']
        restaurant_id=R_ID
        salary=request.POST['salary']
        email=request.POST['email']
        password=request.POST['password']
        e_type=request.POST['e_type']
        with connection.cursor() as cursor:
          cursor.execute("Insert Into employee(restaurant_id,employee_name,salary,email,acc_password,employee_type) values(%s,%s,%s,%s,SHA2(%s,256),%s);",(restaurant_id,employee_name,salary,email,password,e_type))
          cursor.execute('SELECT employee_id from employee where employee_name=%s;',(employee_name,))
          e_id=cursor.fetchone()[0]
          
        if e_type=='SERVER':
            with connection.cursor() as cursor:
             cursor.execute('INSERT INTO e_server values(%s,%s);',(e_id,R_ID))
            
        elif e_type=='KITCHEN_STAFF':
            with connection.cursor() as cursor:
             cursor.execute('INSERT INTO kitchen_staff values(%s,%s)',(e_id,R_ID))

        messages.success(request, "New employee  has been successfully added.")
          
        return redirect('view_employee') 

def employee_detail(request,pk):
    with connection.cursor() as cursor:
        cursor.execute('select * from employee where employee_id=%s and restaurant_id=%s',(pk,R_ID))
        emp=cursor.fetchone()
        
    context={'emp':emp}
    return render(request,'employee_detail.html',context)

def employee_edit(request,pk):
    if request.method=='GET':
         with connection.cursor() as cursor:
          cursor.execute("Select * from employee where employee_id=%s and restaurant_id=%s;",(pk,R_ID,))
          employee=cursor.fetchone()
         context={'emp':employee} 
         return render(request,'edit_employee.html',context)
     
    else:
        employee_name=request.POST['employee_name']
        salary=request.POST['salary']
        email=request.POST['email']
        # password=request.POST['password']
        e_type=request.POST['e_type']
        
        with connection.cursor() as cursor:
          cursor.execute("Update employee set employee_name=%s, salary=%s, email=%s,  employee_type=%s where employee_id=%s and restaurant_id=%s;",(employee_name,salary,email,e_type,pk,R_ID))

        messages.success(request, f"Employee ID {pk}  has been successfully updated.")
          
          
        return redirect('view_employee') 
        
def delete_employee(request,pk):
    with connection.cursor() as cursor:
        cursor.execute('Delete from employee where employee_id=%s and restaurant_id=%s;',(pk,R_ID))

    messages.success(request, f"Employee ID {pk}  has been successfully deleted.")
    
    return redirect('view_employee')       


#inventory
def view_inventory(request):
    query='Select ingredient_id,ingredient_name,unit_price,pruchased_date,expired_date,quantity from inventory natural join ingredient where restaurant_id=%s'
    params=[R_ID]
    i_name=request.GET.get('name',None)
    if i_name:
        query+=" and ingredient_name=%s"
        params.append(i_name)
    with connection.cursor() as cursor:
        cursor.execute(query,params)
        inventories=cursor.fetchall()
          
    context={'inventories':inventories}
    return render(request,'view_inventory.html',context)

def create_inventory(request):
    if request.method=='GET':
     return render(request,'create_inventory.html') 
 
    else:
        
        ingredient_name=request.POST['ingredient_name']
        restaurant_id=R_ID
        price=request.POST['unit_price']
        quantity=request.POST['quantity']
        p_date=request.POST['p_date']
        e_date=request.POST['e_date']
        
        with connection.cursor() as cursor:
            cursor.execute('insert into ingredient(ingredient_name) values(%s);',(ingredient_name,))
            cursor.execute('select ingredient_id from ingredient where ingredient_name=%s;',(ingredient_name,))
            ingredient_id=cursor.fetchone()[0]
        
        with connection.cursor() as cursor:
            cursor.execute('insert into inventory values(%s,%s,%s,%s,%s,%s);',(restaurant_id,ingredient_id,price,p_date,e_date,quantity))

        messages.success(request, f"New Ingredient   has been successfully added to the inventory.")
            
        return redirect('view_inventory')   
    
def edit_inventory(request,pk):
      if request.method=='GET':
        with connection.cursor() as cursor:
            cursor.execute('select  ingredient_id,ingredient_name,unit_price,pruchased_date,expired_date,quantity from inventory natural join ingredient where ingredient_id=%s and restaurant_id=%s;',(pk,R_ID))
            ingredient=cursor.fetchone()
        context={'ingredient':ingredient,}    
        return render(request,'edit_inventory.html',context) 
 
      else:
        ingredient_id=pk
        ingredient_name=request.POST['ingredient_name']
        restaurant_id=R_ID
        price=request.POST['unit_price']
        quantity=request.POST['quantity']
        p_date=request.POST['p_date']
        e_date=request.POST['e_date']
        
        with connection.cursor() as cursor:
            cursor.execute('Update ingredient set ingredient_name=%s where ingredient_id=%s;',(ingredient_name,ingredient_id))
        
        with connection.cursor() as cursor:
            cursor.execute('Update inventory set unit_price=%s, quantity=%s, pruchased_date=%s, expired_date=%s where ingredient_id=%s and restaurant_id=%s;',(price,quantity,p_date,e_date,ingredient_id,restaurant_id))

        messages.success(request, f"Ingredient ID {pk}  has been successfully updated.")
            
        return redirect('view_inventory')
    
def delete_inventory(request,pk):
    with connection.cursor() as cursor:
        cursor.execute('Delete from inventory where ingredient_id=%s and restaurant_id=%s;',(pk,R_ID))
    messages.success(request, f"Ingredient ID {pk}  has been successfully deleted.")
    return redirect('view_inventory')


def sales_report(request):
    start_date = request.GET.get('start_date', datetime.datetime.now().strftime('%Y-%m-01'))  # Default to first day of current month
    end_date = request.GET.get('end_date', datetime.datetime.now().strftime('%Y-%m-%d'))  # Default to today
    # Raw SQL to calculate total revenue
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT SUM(m.price * om.quantity) as total_revenue
            FROM order_menuitem om
            JOIN menu m ON om.menu_item_id = m.menu_item_id
            JOIN menu_item mi ON om.menu_item_id = mi.menu_item_id
            JOIN r_order as ro on om.order_id=ro.order_id
            WHERE m.restaurant_id=%s and ro.order_date between %s and %s;
        ''',(R_ID,start_date,end_date))
        total_revenue = cursor.fetchone()[0] or 0  # If no data, set to 0

    # Raw SQL to get top-selling items
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT mi.menu_name, SUM(om.quantity) as total_sold
            FROM order_menuitem om
            JOIN menu_item mi ON om.menu_item_id = mi.menu_item_id
            JOIN  R_ORDER as ro on ro.order_id=om.order_id
            WHERE ro.restaurant_id=%s
            and ro.order_date between %s and %s
            GROUP BY mi.menu_name
            ORDER BY total_sold DESC
            LIMIT 10
        ''',(R_ID,start_date,end_date))
        top_items = cursor.fetchall() 

    # Format the data for the template
    context = {
        'total_revenue': total_revenue,
        'top_items': [{'menu_name': row[0], 'total_sold': row[1]} for row in top_items],
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render(request, 'reports.html', context)


def inventory_report(request):
    with connection.cursor() as cursor:
        # Query to get the inventory details
        cursor.execute("""
            SELECT 
                i.ingredient_name, 
                inv.quantity, 
                inv.unit_price, 
                inv.pruchased_date, 
                inv.expired_date
            FROM 
                inventory AS inv
            JOIN 
                ingredient AS i ON inv.ingredient_id = i.ingredient_id
            WHERE 
                inv.quantity > 0 and inv.restaurant_id=%s  -- Show only ingredients that are in stock
            ORDER BY 
                inv.expired_date ASC  -- Show the items expiring soonest first
        """,(R_ID,))
        inventory_items = cursor.fetchall()

    return render(request, 'inventory_reports.html', {
        'inventory_items': inventory_items,
    })
       

 
        
        