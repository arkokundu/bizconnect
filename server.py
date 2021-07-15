
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

def clean_input(input):
  cleaned_input = input.replace('"', "").replace("'","")
  return cleaned_input

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
DATABASEURI = "postgresql://ab5051:a@34.73.36.248/project1" # Modify this with your own credentials you received from Joseph!


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
  """

  print("REQUESTS" + str(request.args))
  return render_template("index.html")

@app.route('/search_matches',methods = ['POST'])
def search_matches():
  name = request.form['name']

  if name:
    query_string = '''select c2.connection_timestamp , p."name",b."name"  , 
(CASE WHEN p2.compensation = p3.compensation THEN 1 ELSE 0 END) * 20 +
                (CASE WHEN p2.country = p3.country THEN 1 ELSE 0 END) * 20 +
                (CASE WHEN p2.nature_of_work = p3.nature_of_work THEN 1 ELSE 0 END) * 40 +
                (CASE WHEN p2.duration_of_project = p3.duration_of_project THEN 1 ELSE 0 END) * 20 as score,
                p3.nature_of_work as i_preference_category ,p3.country as i_preference_country,p3.compensation as i_preference_compensation,p3.duration_of_project as i_preference_duration,
          p2.nature_of_work as b_preference_category ,p2.country as b_preference_country,p2.compensation as b_preference_compensation,p2.duration_of_project as b_preference_duration
from "connection" c2 join person p on p.id =c2.individual_id 
left join employee_works_at_business ewab on ewab.employee_id =c2.employee_id
left join business b on b.id =ewab.business_id
left join preferences p2 on p2.entity_id = b.id and p2.entity_type='business'
left join preferences p3 on
	p3.entity_id = c2.individual_id
	and p3.entity_type = 'individual'
	 where p.name = '{}'
order by score desc;

'''.format(name)
  else:
    query_string = '''select * from connection where 1=2;'''
  cursor = g.conn.execute(query_string)
  names = []
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(matches_data=names)
  return render_template("index.html", **context)

@app.route('/business_add')
def business_add():
  return render_template("business_add.html")

@app.route('/business_add_to_db',methods = ['POST'])
def business_add_to_db():

  industry= request.form['industry']
  name = request.form['name']
  domain = request.form['domain'].replace('https://','').replace('www.','')
  year_founded = request.form['year_founded']
  locality = request.form['locality']
  country = request.form['country']
  linkedin = request.form['linkedin'].replace('https://www.','')


  get_max_business_id_query = ''' select max(replace(id,'b_','')::int) from business;'''
  cursor = g.conn.execute(get_max_business_id_query)
  for result in cursor:
    max_id = result[0]

  next_id = 'b_' + str(max_id+1)

  insert_query_string = '''insert into business values('{}','{}','{}','{}','{}','{}','{}','{}')'''\
    .format(next_id,name,domain,year_founded,industry,locality,country,linkedin)

  cursor = g.conn.execute(insert_query_string)
  cursor.close()

  return render_template("business.html")
@app.route('/business_view')
def business_view():
  return render_template("business.html")

@app.route('/business',methods = ['POST'])
def business():
  industry = request.form['industry']
  industry = clean_input(industry)
  name = request.form['name']

  if industry and name:
    query_string = '''SELECT * FROM business where industry = '{}' and name ='{}' limit 100 ;'''.format(industry, name)
  elif industry:
    query_string = '''SELECT * FROM business where industry = '{}'limit 100 ;''' \
      .format(industry)
  elif name:
    query_string = '''SELECT * FROM business where name ='{}' limit 100 ;''' \
      .format(name)
  else:
    query_string = '''SELECT * FROM business limit 100;'''

  cursor = g.conn.execute(query_string)
  names = []
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(business_data=names)
  return render_template("business.html", **context)

@app.route('/person_view')
def person_view():
  return render_template("person.html")

@app.route('/person',methods = ['POST'])
def person():
  category = request.form['category']
  dob = request.form['dob']

  if category and dob:
    query_string = '''select * from person_view where person_identifier = '{}' 
    and date_of_birth >= '{}';'''.format(category,dob)
  elif category:
    query_string = '''select * from person_view where person_identifier = '{}' ;'''\
      .format(category)
  elif dob:
    query_string = '''select * from person_view where date_of_birth >= '{}' ;'''\
      .format(dob)
  else:
    query_string = '''select * from person_view;'''
  cursor = g.conn.execute(query_string)
  person_data = []
  for result in cursor:
    person_data.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(person_data=person_data)
  return render_template("person.html", **context)

@app.route('/connection_view')
def connection_view():
  return render_template("connection.html")

@app.route('/connection',methods = ['POST'])
def connection():
  first_swipe_by = request.form['first_swipe_by']
  first_swipe_by = clean_input(first_swipe_by)

  if first_swipe_by:
    query_string = '''SELECT c.*,case when ch.connection_id is not null then 'true' else 'false' end as chat_interaction, 
case when v.connection_id is not null then 'true' else 'false' end as video_interaction, 
case when pm.connection_id is not null then 'true' else 'false' end as physical_meeting_interaction 
FROM connection c
left join chat ch on ch.connection_id =c.connection_id 
left join video v on c.connection_id =v.connection_id 
left join physical_meeting pm on pm.connection_id = c.connection_id where first_swipe_by = '{}';'''.format(first_swipe_by)
  else:
    query_string = '''SELECT c.*,case when ch.connection_id is not null then 'true' else 'false' end as chat_interaction, 
case when v.connection_id is not null then 'true' else 'false' end as video_interaction, 
case when pm.connection_id is not null then 'true' else 'false' end as physical_meeting_interaction 
FROM connection c
left join chat ch on ch.connection_id =c.connection_id 
left join video v on c.connection_id =v.connection_id 
left join physical_meeting pm on pm.connection_id = c.connection_id;'''
  cursor = g.conn.execute(query_string)
  connection_data = []
  for result in cursor:
    connection_data.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(connection_data=connection_data)
  return render_template("connection.html", **context)

@app.route('/preference_view')
def preference_view():
  return render_template("preference.html")

@app.route('/preference',methods = ['POST'])
def preference():
  nature_of_work = request.form['nature_of_work']
  nature_of_work = clean_input(nature_of_work)
  entity_type = request.form['entity_type']
  entity_type = clean_input(entity_type)
  if nature_of_work and entity_type:
    query_string = '''SELECT * FROM preferences where nature_of_work = '{}' 
     and entity_type >= '{}';'''.format(nature_of_work, entity_type)
  elif nature_of_work:
    query_string = '''SELECT * FROM preferences where nature_of_work = '{}' ;''' \
      .format(nature_of_work)
  elif entity_type:
    query_string = '''SELECT * FROM preferences where entity_type = '{}' ;''' \
      .format(entity_type)
  else:
    query_string = '''SELECT * FROM preferences ;'''

  cursor = g.conn.execute(query_string)
  preference_data = []
  for result in cursor:
    preference_data.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(preference_data=preference_data)
  return render_template("preference.html", **context)

@app.route('/chat_view')
def chat_view():
  return render_template("chat.html")

@app.route('/chat',methods = ['POST'])
def chat():
  connection_id = request.form['connection_id']
  connection_id = clean_input(connection_id)

  if connection_id:
    query_string = '''SELECT * FROM chat where connection_id = '{}' ;'''.format(connection_id)
  else:
    query_string = '''SELECT * FROM chat;'''
  cursor = g.conn.execute(query_string)
  chat_data = []
  for result in cursor:
    chat_data.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(chat_data=chat_data)
  return render_template("chat.html", **context)

@app.route('/video_view')
def video_view():
  return render_template("video.html")

@app.route('/video',methods = ['POST'])
def video():
  connection_id = request.form['connection_id']
  connection_id = clean_input(connection_id)

  if connection_id:
    query_string = '''SELECT * FROM video where connection_id = '{}';'''.format(connection_id)
  else:
    query_string = '''SELECT * FROM video ;'''
  cursor = g.conn.execute(query_string)
  video_data = []
  for result in cursor:
    video_data.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(video_data=video_data)
  return render_template("video.html", **context)

@app.route('/physical_view')
def physical_view():
  return render_template("physical.html")

@app.route('/physical',methods = ['POST'])
def physical():
  connection_id = request.form['connection_id']
  connection_id = clean_input(connection_id)

  if connection_id:
    query_string = '''SELECT * FROM physical_meeting where connection_id = '{}' ;'''.format(connection_id)
  else:
    query_string = '''SELECT * FROM physical_meeting ;'''
  cursor = g.conn.execute(query_string)
  physical_data = []
  for result in cursor:
    physical_data.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(physical_data=physical_data)
  return render_template("physical.html", **context)


# @app.route('/add', methods=['POST'])
# def add():
#
#   name = request.form['name']
#   g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
#   return redirect('/')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
