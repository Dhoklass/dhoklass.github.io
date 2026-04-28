from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from functools import wraps
import random, string

app = Flask(__name__)
app.config.from_object(Config)
mysql = MySQL(app)

# ── Helpers ──────────────────────────────────────────────────────────────────

def gen_ref():
    return 'GF-' + ''.join(random.choices(string.digits, k=6))

def login_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get('role') != role:
                flash('Please log in to continue.', 'warning')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return wrapper
    return decorator

def cur():
    return mysql.connection.cursor()

# ── Seed ─────────────────────────────────────────────────────────────────────

@app.route('/seed')
def seed():
    c = cur()
    c.execute("SELECT COUNT(*) AS n FROM categories")
    if c.fetchone()['n'] == 0:
        cats = [
            ('Slow PC / Performance','fa-gauge-high'),
            ('Blue Screen / Crash','fa-skull-crossbones'),
            ('Virus / Malware','fa-bug'),
            ('WiFi / Network Issue','fa-wifi'),
            ('Driver Problem','fa-microchip'),
            ('Printer Issue','fa-print'),
            ('Software Installation','fa-download'),
            ('System Error','fa-triangle-exclamation'),
            ('Data Recovery','fa-hard-drive'),
            ('Other','fa-circle-question'),
        ]
        c.executemany("INSERT INTO categories(name,icon) VALUES(%s,%s)", cats)

    c.execute("SELECT COUNT(*) AS n FROM admins")
    if c.fetchone()['n'] == 0:
        c.execute("INSERT INTO admins(name,email,password_hash) VALUES(%s,%s,%s)",
                  ('GlitchFix Admin','admin@glitchfix.com',generate_password_hash('Admin@123')))

    c.execute("SELECT COUNT(*) AS n FROM engineers")
    if c.fetchone()['n'] == 0:
        for e in [
            ('Arjun Mehta','arjun@glitchfix.com','Windows & Driver Issues'),
            ('Priya Sharma','priya@glitchfix.com','Networking & WiFi'),
            ('Rohan Das','rohan@glitchfix.com','Malware & Security'),
        ]:
            c.execute("INSERT INTO engineers(name,email,password_hash,specialization) VALUES(%s,%s,%s,%s)",
                      (e[0],e[1],generate_password_hash('Engineer@123'),e[2]))

    c.execute("SELECT COUNT(*) AS n FROM users")
    if c.fetchone()['n'] == 0:
        for u in [
            ('Amit Kulkarni','amit@example.com','9876543210'),
            ('Sneha Patil','sneha@example.com','9123456789'),
            ('Vijay Tiwari','vijay@example.com','9988776655'),
            ('Kavya Nair','kavya@example.com','9011223344'),
        ]:
            c.execute("INSERT INTO users(name,email,password_hash,phone) VALUES(%s,%s,%s,%s)",
                      (u[0],u[1],generate_password_hash('User@123'),u[2]))

    mysql.connection.commit()

    c.execute("SELECT COUNT(*) AS n FROM tickets")
    if c.fetchone()['n'] == 0:
        c.execute("SELECT id FROM users LIMIT 4"); uids=[r['id'] for r in c.fetchall()]
        c.execute("SELECT id FROM engineers LIMIT 3"); eids=[r['id'] for r in c.fetchall()]
        c.execute("SELECT id FROM categories LIMIT 10"); cids=[r['id'] for r in c.fetchall()]

        tickets = [
            (uids[0],eids[0],cids[0],'PC running extremely slow','My laptop has been extremely slow for a week. Takes 10 min to boot.','Laptop','Windows 11','High','In Progress','123456789','tmppass1'),
            (uids[0],None,cids[2],'Possible virus infection','Strange pop-ups and browser redirects to unknown sites.','Desktop','Windows 10','Critical','Open','',''),
            (uids[1],eids[1],cids[3],'WiFi disconnects randomly','WiFi drops every 30 minutes and I have to manually reconnect.','Laptop','Windows 11','Medium','Assigned','987654321','tmppass2'),
            (uids[1],eids[0],cids[1],'Blue screen on startup','Getting BSOD IRQL_NOT_LESS_OR_EQUAL almost every day.','Desktop','Windows 10','Critical','Resolved','112233445','tmppass3'),
            (uids[2],None,cids[4],'Graphics driver not working','After Windows update my graphics driver stopped working.','Laptop','Windows 11','Medium','Under Review','',''),
            (uids[2],eids[2],cids[6],'Cannot install Adobe Creative Cloud','Keeps giving error code 101 on every attempt.','Desktop','Windows 10','Low','In Progress','556677889','tmppass4'),
            (uids[3],eids[1],cids[5],'HP Printer not detected','Printer not being detected by Windows. Reinstalled drivers, still fails.','Desktop','Windows 11','Medium','Waiting for User','998877665','tmppass5'),
            (uids[3],None,cids[7],'System keeps restarting randomly','Random restarts every few hours with no error message.','Laptop','Windows 10','High','Open','',''),
        ]
        for t in tickets:
            ref = gen_ref()
            c.execute("""INSERT INTO tickets(ticket_ref,user_id,engineer_id,category_id,title,description,
                device_type,operating_system,priority,status,rustdesk_id,rustdesk_password)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (ref,t[0],t[1],t[2],t[3],t[4],t[5],t[6],t[7],t[8],t[9],t[10]))

        mysql.connection.commit()
        c.execute("SELECT id,status,engineer_id FROM tickets")
        for t in c.fetchall():
            if t['status'] in ('In Progress','Resolved','Assigned','Waiting for User'):
                c.execute("INSERT INTO ticket_updates(ticket_id,author_role,author_id,message) VALUES(%s,'admin',1,%s)",
                          (t['id'],'Ticket received and reviewed. Engineer will be assigned shortly.'))
            if t['status'] in ('In Progress','Resolved') and t['engineer_id']:
                c.execute("INSERT INTO ticket_updates(ticket_id,author_role,author_id,message) VALUES(%s,'engineer',%s,%s)",
                          (t['id'],t['engineer_id'],'Hello! I have reviewed your issue. Please keep RustDesk open so I can connect remotely.'))
            if t['status'] == 'Resolved':
                c.execute("INSERT INTO ticket_updates(ticket_id,author_role,author_id,message) VALUES(%s,'engineer',%s,%s)",
                          (t['id'],t['engineer_id'],'Issue resolved successfully. Let us know if it occurs again. Have a great day!'))
                c.execute("UPDATE tickets SET fix_summary=%s WHERE id=%s",
                          ('Identified and resolved the root cause via remote session. System is now stable.',t['id']))
        mysql.connection.commit()

    c.close()
    flash('Sample data seeded successfully!', 'success')
    return redirect(url_for('index'))

# ── Public ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# ── Auth ──────────────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email'].strip().lower()
        password = request.form['password']
        role     = request.form.get('role','user')
        table    = {'user':'users','admin':'admins','engineer':'engineers'}.get(role)
        if not table:
            flash('Invalid role selected.','danger')
            return redirect(url_for('login'))
        c = cur()
        c.execute(f"SELECT * FROM {table} WHERE email=%s", (email,))
        user = c.fetchone(); c.close()
        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['role']       = role
            session['user_id']    = user['id']
            session['user_name']  = user['name']
            session['user_email'] = user['email']
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for(f'{role}_dashboard'))
        flash('Incorrect email or password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name    = request.form['name'].strip()
        email   = request.form['email'].strip().lower()
        phone   = request.form.get('phone','').strip()
        pw      = request.form['password']
        confirm = request.form['confirm_password']
        if pw != confirm:
            flash('Passwords do not match.','danger')
            return redirect(url_for('register'))
        c = cur()
        c.execute("SELECT id FROM users WHERE email=%s",(email,))
        if c.fetchone():
            flash('Email already registered. Please log in.','warning')
            c.close()
            return redirect(url_for('register'))
        c.execute("INSERT INTO users(name,email,password_hash,phone) VALUES(%s,%s,%s,%s)",
                  (name,email,generate_password_hash(pw),phone))
        mysql.connection.commit(); c.close()
        flash('Account created successfully! Please log in.','success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.','info')
    return redirect(url_for('index'))

# ── User ──────────────────────────────────────────────────────────────────────

@app.route('/user/dashboard')
@login_required('user')
def user_dashboard():
    uid = session['user_id']
    c = cur()
    c.execute("SELECT COUNT(*) AS n FROM tickets WHERE user_id=%s",(uid,)); total=c.fetchone()['n']
    c.execute("SELECT COUNT(*) AS n FROM tickets WHERE user_id=%s AND status='Open'",(uid,)); open_t=c.fetchone()['n']
    c.execute("SELECT COUNT(*) AS n FROM tickets WHERE user_id=%s AND status='Resolved'",(uid,)); resolved=c.fetchone()['n']
    c.execute("SELECT COUNT(*) AS n FROM tickets WHERE user_id=%s AND status NOT IN('Open','Resolved','Closed','Cancelled')",(uid,)); in_prog=c.fetchone()['n']
    c.execute("""SELECT t.*,c.name AS cat_name FROM tickets t
        LEFT JOIN categories c ON t.category_id=c.id
        WHERE t.user_id=%s ORDER BY t.updated_at DESC LIMIT 6""",(uid,))
    recent=c.fetchall()
    c.execute("SELECT * FROM notifications WHERE user_id=%s AND is_read=0 ORDER BY created_at DESC LIMIT 5",(uid,))
    notifs=c.fetchall(); c.close()
    return render_template('user_dashboard.html',total=total,open_t=open_t,
        resolved=resolved,in_prog=in_prog,recent=recent,notifs=notifs)

@app.route('/user/tickets')
@login_required('user')
def user_tickets():
    uid=session['user_id']; sf=request.args.get('status','')
    c=cur()
    if sf:
        c.execute("""SELECT t.*,c.name AS cat_name FROM tickets t
            LEFT JOIN categories c ON t.category_id=c.id
            WHERE t.user_id=%s AND t.status=%s ORDER BY t.updated_at DESC""",(uid,sf))
    else:
        c.execute("""SELECT t.*,c.name AS cat_name FROM tickets t
            LEFT JOIN categories c ON t.category_id=c.id
            WHERE t.user_id=%s ORDER BY t.updated_at DESC""",(uid,))
    tickets=c.fetchall(); c.close()
    return render_template('user_tickets.html',tickets=tickets,status_filter=sf)

@app.route('/user/ticket/<int:tid>')
@login_required('user')
def user_ticket_detail(tid):
    uid=session['user_id']; c=cur()
    c.execute("""SELECT t.*,c.name AS cat_name,e.name AS eng_name,e.specialization AS eng_spec
        FROM tickets t LEFT JOIN categories c ON t.category_id=c.id
        LEFT JOIN engineers e ON t.engineer_id=e.id
        WHERE t.id=%s AND t.user_id=%s""",(tid,uid))
    ticket=c.fetchone()
    if not ticket:
        flash('Ticket not found.','danger'); c.close()
        return redirect(url_for('user_tickets'))
    c.execute(_updates_sql(),(tid,)); updates=c.fetchall(); c.close()
    return render_template('ticket_detail.html',ticket=ticket,updates=updates,role='user')

@app.route('/user/ticket/<int:tid>/reply', methods=['POST'])
@login_required('user')
def user_reply(tid):
    msg=request.form.get('message','').strip()
    if msg:
        c=cur()
        c.execute("INSERT INTO ticket_updates(ticket_id,author_role,author_id,message) VALUES(%s,'user',%s,%s)",
                  (tid,session['user_id'],msg))
        mysql.connection.commit(); c.close()
        flash('Reply sent.','success')
    return redirect(url_for('user_ticket_detail',tid=tid))

@app.route('/user/create-ticket', methods=['GET','POST'])
@login_required('user')
def create_ticket():
    c=cur(); c.execute("SELECT * FROM categories"); cats=c.fetchall()
    if request.method=='POST':
        f=request.form; ref=gen_ref()
        c.execute("""INSERT INTO tickets(ticket_ref,user_id,category_id,title,description,
            device_type,operating_system,priority,rustdesk_id,rustdesk_password,preferred_time)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (ref,session['user_id'],f.get('category_id') or None,
             f['title'],f['description'],f['device_type'],
             f['operating_system'],f['priority'],
             f.get('rustdesk_id',''),f.get('rustdesk_password',''),f.get('preferred_time','')))
        mysql.connection.commit()
        c.execute("SELECT id FROM tickets WHERE ticket_ref=%s",(ref,))
        new_id=c.fetchone()['id']
        c.execute("INSERT INTO ticket_updates(ticket_id,author_role,author_id,message) VALUES(%s,'user',%s,'Ticket submitted successfully.')",
                  (new_id,session['user_id']))
        mysql.connection.commit(); c.close()
        flash(f'Ticket {ref} created successfully!','success')
        return redirect(url_for('user_tickets'))
    c.close()
    return render_template('create_ticket.html',categories=cats)

@app.route('/user/profile', methods=['GET','POST'])
@login_required('user')
def user_profile():
    c=cur()
    if request.method=='POST':
        c.execute("UPDATE users SET name=%s,phone=%s WHERE id=%s",
                  (request.form['name'],request.form.get('phone',''),session['user_id']))
        mysql.connection.commit()
        session['user_name']=request.form['name']
        flash('Profile updated successfully.','success')
    c.execute("SELECT * FROM users WHERE id=%s",(session['user_id'],))
    user=c.fetchone(); c.close()
    return render_template('profile.html',user=user)

# ── Admin ─────────────────────────────────────────────────────────────────────

@app.route('/admin/dashboard')
@login_required('admin')
def admin_dashboard():
    c=cur()
    c.execute("SELECT COUNT(*) AS n FROM tickets"); total=c.fetchone()['n']
    c.execute("SELECT COUNT(*) AS n FROM tickets WHERE status='Open'"); open_t=c.fetchone()['n']
    c.execute("SELECT COUNT(*) AS n FROM tickets WHERE status='Resolved'"); resolved=c.fetchone()['n']
    c.execute("SELECT COUNT(*) AS n FROM tickets WHERE status='In Progress'"); in_prog=c.fetchone()['n']
    c.execute("SELECT COUNT(*) AS n FROM users"); user_count=c.fetchone()['n']
    c.execute("SELECT COUNT(*) AS n FROM engineers"); eng_count=c.fetchone()['n']
    c.execute("""SELECT t.*,u.name AS user_name,c.name AS cat_name,e.name AS eng_name
        FROM tickets t LEFT JOIN users u ON t.user_id=u.id
        LEFT JOIN categories c ON t.category_id=c.id
        LEFT JOIN engineers e ON t.engineer_id=e.id
        ORDER BY t.updated_at DESC LIMIT 10""")
    recent=c.fetchall(); c.close()
    return render_template('admin_dashboard.html',total=total,open_t=open_t,
        resolved=resolved,in_prog=in_prog,user_count=user_count,eng_count=eng_count,recent=recent)

@app.route('/admin/tickets')
@login_required('admin')
def admin_tickets():
    c=cur(); q=request.args.get('q',''); status=request.args.get('status',''); priority=request.args.get('priority','')
    sql="""SELECT t.*,u.name AS user_name,c.name AS cat_name,e.name AS eng_name
        FROM tickets t LEFT JOIN users u ON t.user_id=u.id
        LEFT JOIN categories c ON t.category_id=c.id
        LEFT JOIN engineers e ON t.engineer_id=e.id WHERE 1=1"""
    params=[]
    if q: sql+=" AND(t.title LIKE %s OR t.ticket_ref LIKE %s OR u.name LIKE %s)"; params+=[f'%{q}%']*3
    if status: sql+=" AND t.status=%s"; params.append(status)
    if priority: sql+=" AND t.priority=%s"; params.append(priority)
    sql+=" ORDER BY t.updated_at DESC"
    c.execute(sql,params); tickets=c.fetchall(); c.close()
    return render_template('admin_tickets.html',tickets=tickets,q=q,status=status,priority=priority)

@app.route('/admin/ticket/<int:tid>', methods=['GET','POST'])
@login_required('admin')
def admin_ticket_detail(tid):
    c=cur()
    c.execute("""SELECT t.*,u.name AS user_name,u.email AS user_email,
        c.name AS cat_name,e.name AS eng_name
        FROM tickets t LEFT JOIN users u ON t.user_id=u.id
        LEFT JOIN categories c ON t.category_id=c.id
        LEFT JOIN engineers e ON t.engineer_id=e.id WHERE t.id=%s""",(tid,))
    ticket=c.fetchone()
    if not ticket:
        flash('Ticket not found.','danger'); c.close()
        return redirect(url_for('admin_tickets'))
    c.execute("SELECT * FROM engineers WHERE is_active=1"); engineers=c.fetchall()
    c.execute(_updates_sql(),(tid,)); updates=c.fetchall()
    if request.method=='POST':
        action=request.form.get('action')
        if action=='assign':
            eid=request.form['engineer_id']
            c.execute("UPDATE tickets SET engineer_id=%s,status='Assigned' WHERE id=%s",(eid,tid))
            c.execute("SELECT name FROM engineers WHERE id=%s",(eid,))
            eng=c.fetchone()
            c.execute("INSERT INTO ticket_updates(ticket_id,author_role,author_id,message) VALUES(%s,'admin',1,%s)",
                      (tid,f'Ticket assigned to engineer: {eng["name"]}'))
            c.execute("SELECT user_id FROM tickets WHERE id=%s",(tid,))
            uid=c.fetchone()['user_id']
            c.execute("INSERT INTO notifications(user_id,message) VALUES(%s,'Your ticket has been assigned to an engineer.')",(uid,))
        elif action=='status':
            ns=request.form['status']
            c.execute("UPDATE tickets SET status=%s WHERE id=%s",(ns,tid))
            c.execute("INSERT INTO ticket_updates(ticket_id,author_role,author_id,message) VALUES(%s,'admin',1,%s)",
                      (tid,f'Status updated to: {ns}'))
            c.execute("SELECT user_id FROM tickets WHERE id=%s",(tid,))
            uid=c.fetchone()['user_id']
            c.execute("INSERT INTO notifications(user_id,message) VALUES(%s,%s)",(uid,f'Your ticket status changed to: {ns}'))
        elif action=='message':
            msg=request.form.get('message','').strip()
            if msg:
                c.execute("INSERT INTO ticket_updates(ticket_id,author_role,author_id,message) VALUES(%s,'admin',1,%s)",(tid,msg))
                c.execute("SELECT user_id FROM tickets WHERE id=%s",(tid,))
                uid=c.fetchone()['user_id']
                c.execute("INSERT INTO notifications(user_id,message) VALUES(%s,'Admin has sent an update on your ticket.')",(uid,))
        elif action=='delete':
            c.execute("DELETE FROM tickets WHERE id=%s",(tid,))
            mysql.connection.commit(); c.close()
            flash('Ticket deleted successfully.','success')
            return redirect(url_for('admin_tickets'))
        mysql.connection.commit()
        flash('Action performed successfully.','success')
        return redirect(url_for('admin_ticket_detail',tid=tid))
    c.close()
    return render_template('admin_ticket_detail.html',ticket=ticket,engineers=engineers,updates=updates)

@app.route('/admin/engineers', methods=['GET','POST'])
@login_required('admin')
def admin_engineers():
    c=cur()
    if request.method=='POST':
        action=request.form.get('action')
        if action=='add':
            name=request.form['name']; email=request.form['email'].lower()
            c.execute("SELECT id FROM engineers WHERE email=%s",(email,))
            if c.fetchone():
                flash('Email already exists.','danger')
            else:
                c.execute("INSERT INTO engineers(name,email,password_hash,specialization) VALUES(%s,%s,%s,%s)",
                          (name,email,generate_password_hash(request.form['password']),request.form.get('specialization','')))
                flash('Engineer added successfully.','success')
        elif action=='toggle':
            c.execute("UPDATE engineers SET is_active=1-is_active WHERE id=%s",(request.form['engineer_id'],))
            flash('Engineer status updated.','success')
        elif action=='delete':
            c.execute("DELETE FROM engineers WHERE id=%s",(request.form['engineer_id'],))
            flash('Engineer removed.','success')
        mysql.connection.commit()
        return redirect(url_for('admin_engineers'))
    c.execute("""SELECT e.*,COUNT(t.id) AS ticket_count FROM engineers e
        LEFT JOIN tickets t ON e.id=t.engineer_id GROUP BY e.id ORDER BY e.created_at DESC""")
    engineers=c.fetchall(); c.close()
    return render_template('admin_engineers.html',engineers=engineers)

@app.route('/admin/users')
@login_required('admin')
def admin_users():
    c=cur()
    c.execute("""SELECT u.*,COUNT(t.id) AS ticket_count FROM users u
        LEFT JOIN tickets t ON u.id=t.user_id GROUP BY u.id ORDER BY u.created_at DESC""")
    users=c.fetchall(); c.close()
    return render_template('admin_users.html',users=users)

# ── Engineer ──────────────────────────────────────────────────────────────────

@app.route('/engineer/dashboard')
@login_required('engineer')
def engineer_dashboard():
    eid=session['user_id']; c=cur()
    c.execute("SELECT COUNT(*) AS n FROM tickets WHERE engineer_id=%s",(eid,)); total=c.fetchone()['n']
    c.execute("SELECT COUNT(*) AS n FROM tickets WHERE engineer_id=%s AND status='In Progress'",(eid,)); in_prog=c.fetchone()['n']
    c.execute("SELECT COUNT(*) AS n FROM tickets WHERE engineer_id=%s AND status='Resolved'",(eid,)); resolved=c.fetchone()['n']
    c.execute("SELECT COUNT(*) AS n FROM tickets WHERE engineer_id=%s AND status='Assigned'",(eid,)); new_t=c.fetchone()['n']
    c.execute("""SELECT t.*,u.name AS user_name,c.name AS cat_name
        FROM tickets t LEFT JOIN users u ON t.user_id=u.id
        LEFT JOIN categories c ON t.category_id=c.id
        WHERE t.engineer_id=%s ORDER BY t.updated_at DESC""",(eid,))
    tickets=c.fetchall(); c.close()
    return render_template('engineer_dashboard.html',total=total,in_prog=in_prog,
        resolved=resolved,new_t=new_t,tickets=tickets)

@app.route('/engineer/ticket/<int:tid>', methods=['GET','POST'])
@login_required('engineer')
def engineer_ticket_detail(tid):
    eid=session['user_id']; c=cur()
    c.execute("""SELECT t.*,u.name AS user_name,u.email AS user_email,c.name AS cat_name
        FROM tickets t LEFT JOIN users u ON t.user_id=u.id
        LEFT JOIN categories c ON t.category_id=c.id
        WHERE t.id=%s AND t.engineer_id=%s""",(tid,eid))
    ticket=c.fetchone()
    if not ticket:
        flash('Ticket not found or not assigned to you.','danger'); c.close()
        return redirect(url_for('engineer_dashboard'))
    c.execute(_updates_sql(),(tid,)); updates=c.fetchall()
    if request.method=='POST':
        action=request.form.get('action')
        if action=='status':
            ns=request.form['status']
            c.execute("UPDATE tickets SET status=%s WHERE id=%s",(ns,tid))
            if ns=='Resolved':
                c.execute("UPDATE tickets SET fix_summary=%s WHERE id=%s",(request.form.get('fix_summary',''),tid))
            c.execute("INSERT INTO ticket_updates(ticket_id,author_role,author_id,message) VALUES(%s,'engineer',%s,%s)",
                      (tid,eid,f'Status updated to: {ns}'))
            c.execute("SELECT user_id FROM tickets WHERE id=%s",(tid,))
            uid=c.fetchone()['user_id']
            c.execute("INSERT INTO notifications(user_id,message) VALUES(%s,%s)",(uid,f'Your ticket status changed to: {ns}'))
        elif action=='message':
            msg=request.form.get('message','').strip()
            if msg:
                c.execute("INSERT INTO ticket_updates(ticket_id,author_role,author_id,message) VALUES(%s,'engineer',%s,%s)",
                          (tid,eid,msg))
        mysql.connection.commit()
        flash('Updated successfully.','success')
        return redirect(url_for('engineer_ticket_detail',tid=tid))
    c.close()
    return render_template('ticket_detail.html',ticket=ticket,updates=updates,role='engineer')

# ── API ───────────────────────────────────────────────────────────────────────

@app.route('/api/notifications/read', methods=['POST'])
def mark_notifs_read():
    if session.get('role')=='user':
        c=cur()
        c.execute("UPDATE notifications SET is_read=1 WHERE user_id=%s",(session['user_id'],))
        mysql.connection.commit(); c.close()
    return jsonify({'ok':True})

# ── Helper SQL ────────────────────────────────────────────────────────────────

def _updates_sql():
    return """SELECT u.message,u.author_role,u.created_at,
        CASE u.author_role
          WHEN 'user' THEN (SELECT name FROM users WHERE id=u.author_id)
          WHEN 'admin' THEN (SELECT name FROM admins WHERE id=u.author_id)
          WHEN 'engineer' THEN (SELECT name FROM engineers WHERE id=u.author_id)
        END AS author_name
        FROM ticket_updates u WHERE u.ticket_id=%s ORDER BY u.created_at ASC"""

if __name__ == '__main__':
    app.run(debug=True)
