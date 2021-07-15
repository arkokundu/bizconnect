create table business
(id varchar(64),
name varchar(200) not null,
domain varchar(30),
year_founded numeric(4,0),
industry varchar(20),
locality varchar(30),
country varchar(30),
linkedin_url varchar(30),
primary key(id));

create table person
(id varchar(64),
ssn char(9),
name varchar(200) not null,
email varchar(64),
date_of_birth date,
--age interval generated always as (current_date - date_of_birth) stored check (age>18),
phone_number numeric(10,0),
address varchar(30),
city varchar(30),
state varchar(30),
zip numeric(5,0),
primary key(id, email));

create table individual(
individual_id varchar(64),
person_id varchar(64),
linkedin_url varchar(30),
primary key (individual_id,personal_id),
foreign key (person_id) references person(id)
);

create table employee(
employee_id varchar(64),
person_id varchar(64),
ssn char(9),
business_id varchar(64),
employee_start_date date,
primary key (employee_id),
foreign key (person_id) references person(id)
foreign key (business_id) references employee_works_at_business);

create table empl_matches_connection(
employee_id varchar(64),
connection_id varchar(64),
primary key (employee_id,connection_id),
foreign key (employee_id) references employee,
foreign key (connection_id) references connection);

create table indiv_matches_connection(
individual_id varchar(64),
connection_id varchar(64),
primary key (individual_id,connection_id),
foreign key (individual_id) references individual,
foreign key (connection_id) references connection);

create table employee_works_at_business(
employee_id varchar(64),
business_id varchar(64)
primary key(employee_id,business_id),
foreign key (employee_id) references employee,
foreign key (business_id) references business);

create table preferences(
preference_id varchar(64),
entity_type varchar(64) check (entity_type in (‘business’,’individual’)),
entity_id varchar(64),
country varchar(30),
nature_of_work varchar(64),
compensation numeric(12,0)
duration_of_project numeric(4,0),
primary key(preference_id));

create table business_defined_preferences(
business_id varchar(64),
preference_id varchar(64),
primary key(business_id,preference_id),
foreign key (preference_id) references preference
foreign key(business_id) references business(id));

create table indiv_defines_preferences(
individual_id varchar(64),
preference_id varchar(64),
primary key(individual_id,preference_id),
foreign key (preference_id) references preference
foreign key (individual_id) references individual);




create table connection(
connection_id varchar(64),
connection_timestamp timestamp,
first_swipe_by_type varchar(20) check (first_swipe_by_type in (‘business’,’individual’)),,
first_swipe_by_type_id varchar(64),
second_swipe_by_type varchar(20) check (second_swipe_by_type in (‘business’,’individual’)),,
second_swipe_by_type_id varchar(64),
primary key (connection_id));

create table chat(
chat_id varchar(64),
connection_id varchar(64),
chat_duration interval generated always as (chat_end_time - chat_start_time) stored,
chat_text varchar(500),
no_of_messages numeric(5,0),
chat_start_time timestamp ,
chat_end_time timestamp ,
primary key(chat_id),
foreign key (connection_id ) references (connection));

create table video(
video_id varchar(64),
connection_id varchar(64),
video_duration interval generated always as (video_end_time - video_start_time) stored,
network _ping varchar(5),
quality varchar(10),
video_on_flag numeric(1,0),
video_start_time timestamp ,
video_end_time timestamp ,
primary key (video_id),
foreign key (connection_id ) references (connection));

create table physical_meeting(
meeting_id varchar(64),
connection_id varchar(64),
location varchar(100),
primary key (meeting_id),
foreign key (connection_id ) references (connection));
