-- -- \. C:\Users\basti\Documents\assessment\budget.sql

drop database IF EXISTS budget;
create database budget;
use budget;

drop table IF EXISTS user;
drop table IF EXISTS budget;
drop table IF EXISTS expense;
drop table IF EXISTS purchase;
drop table IF EXISTS create_budget;
drop table IF EXISTS create_expense;
drop table IF EXISTS create_purchase;
DROP PROCEDURE IF EXISTS GETUSER;
DROP PROCEDURE IF EXISTS GETBUDGET;
DROP PROCEDURE IF EXISTS GETBUDGET_DETAILS;
DROP PROCEDURE IF EXISTS GETEXPENSE;
DROP PROCEDURE IF EXISTS GETPURCHASE;





create table user(
	id int auto_increment not null,
    name varchar(100) not null,
    email varchar(65) not null,
    password varchar(255),
admin BOOLEAN DEFAULT 0, 
    
    primary key(id)
);



create table budget(
	id int auto_increment not null,
    name varchar(100) ,
    income decimal (20, 2),
    date datetime,
    primary key(id)
);




create table create_budget
   (user_id 	int	, 
    budget_id		int,
    date 		datetime	not null,
 
    primary key(user_id,budget_id),
    foreign key(user_id) references user(id) on update cascade on delete cascade,
	foreign key(budget_id) references budget(id) on update cascade on delete cascade);




create table expense(
	id int auto_increment not null,
    name varchar(100) ,
    allocation decimal (20, 2),
    date datetime,
    
    primary key(id)
);


create table purchase(
	id int auto_increment not null,
    name varchar(100) ,
    cost decimal (20, 2),
    date datetime,
    primary key(id)
);




create table create_expense
   (budget_id 	int	, 
    expense_id		int,
    date 		datetime	not null,
 
    primary key(budget_id,expense_id),
    foreign key(budget_id) references budget(id) on update cascade on delete cascade,
	foreign key(expense_id) references expense(id) on update cascade on delete cascade);

create table create_purchase
   (expense_id 	int	, 
    purchase_id		int,
    date 		datetime	not null,
 
    primary key(expense_id,purchase_id	),
    foreign key(expense_id) references expense(id) on update cascade on delete cascade,
	foreign key(purchase_id	) references purchase(id) on update cascade on delete cascade);





-- -- INSERT INTO TABLE USER
Insert into user values(1,'Speur Admin','admin@speurgroup.com','sha256$QRHf8sjm$ce7a086a61cc09c524d884974ff795d439340305a9d01e95c54228ffad6f572d',1);
Insert into user values(2,'Alex Admin','alex@gmail.com','sha256$QRHf8sjm$ce7a086a61cc09c524d884974ff795d439340305a9d01e95c54228ffad6f572d',1);
Insert into user values(3,'Alex Grant','alexgrant@gmail.com','sha256$VXpnhS77$6660e87181ffabd358234888328cd2f1343d370531a9f5d4eb6e18751d7ef5c5',0 );
Insert into user values(4,'Ray Turner','rayturner@gmail.com','sha256$VXpnhS77$6660e87181ffabd358234888328cd2f1343d370531a9f5d4eb6e18751d7ef5c5',0);
Insert into user values(5,'Diandra Brown','diandra.b@gmail.com','sha256$VXpnhS77$6660e87181ffabd358234888328cd2f1343d370531a9f5d4eb6e18751d7ef5c5',0 );
Insert into user values(6,'Garfield Grant','bastic@gmail.com','sha256$VXpnhS77$6660e87181ffabd358234888328cd2f1343d370531a9f5d4eb6e18751d7ef5c5',0);
Insert into user values(7,'Ashley Francis','ashleyfrancis@gmail.com','sha256$VXpnhS77$6660e87181ffabd358234888328cd2f1343d370531a9f5d4eb6e18751d7ef5c5',0 );
Insert into user values(8,'Jordan Williams','jordan123@gmail.com','sha256$VXpnhS77$6660e87181ffabd358234888328cd2f1343d370531a9f5d4eb6e18751d7ef5c5',0);

-- -- INSERT INTO TABLE BUDGET
Insert into budget values(1,'car budget',350000.00,'2020-06-01 01:59:26.310344' );
Insert into budget values(2,'house budget',350000.00,'2020-06-01 01:59:26.310344');
Insert into budget values(3,'laptop budget',55000.00,'2020-06-01 01:59:26.310344');
 Insert into budget values(4,'vehicle budget',55000.00,'2020-06-01 01:59:26.310344');
 Insert into budget values(5,'miscellaneous',62000.00,'2020-06-01 01:59:26.310344' );
Insert into budget values(6,'gaming laptop',62000.00,'2020-06-01 01:59:26.310344');
Insert into budget values(7,'laptop budget',95000.00,'2020-06-01 01:59:26.310344');
 Insert into budget values(8,'maintainace',95000.00,'2020-06-01 01:59:26.310344');
 Insert into budget values(9,'new phone',750000.00,'2020-06-01 01:59:26.310344' );
Insert into budget values(10,'house budget',750000.00,'2020-06-01 01:59:26.310344');
Insert into budget values(11,'laptop budget',87550.00,'2020-06-01 01:59:26.310344');
 Insert into budget values(12,'main budget',87550.00,'2020-06-01 01:59:26.310344');


-- -- INSERT INTO RELATIONSHIP CREATE BUDGET
Insert into create_budget values(3,1,'2020-06-01 01:59:26.310344' );
Insert into create_budget values(3,2, '2020-06-01 01:59:26.310344');
Insert into create_budget values(4,3, '2020-06-01 01:59:26.310344');
Insert into create_budget values(4,4, '2020-06-01 01:59:26.310344');
Insert into create_budget values(5,5,'2020-06-01 01:59:26.310344' );
Insert into create_budget values(5,6, '2020-06-01 01:59:26.310344');
Insert into create_budget values(6,7, '2020-06-01 01:59:26.310344');
Insert into create_budget values(6,8, '2020-06-01 01:59:26.310344');
Insert into create_budget values(7,9,'2020-06-01 01:59:26.310344' );
Insert into create_budget values(7,10, '2020-06-01 01:59:26.310344');
Insert into create_budget values(8,11, '2020-06-01 01:59:26.310344');
Insert into create_budget values(8,12, '2020-06-01 01:59:26.310344');



-- -- INSERT INTO TABLE EXPENSE
Insert into expense values(1,'2019 car model',30000.00,'2020-06-01 01:59:26.310344' );
Insert into expense values(2,'car rims',10000.00,'2020-06-01 01:59:26.310344');
Insert into expense values(3,'new house in miami',130000.00,'2020-06-01 01:59:26.310344');
Insert into expense values(4,'mercedez benz clk',50000.00,'2020-06-01 01:59:26.310344');
Insert into expense values(5,'vacation',10000.00,'2020-06-01 01:59:26.310344');
Insert into expense values(6,'razor laptop',1500.00,'2020-06-01 01:59:26.310344');
Insert into expense values(7,'laptop',1000.00,'2020-06-01 01:59:26.310344');
Insert into expense values(8,'vehicle maintainace',2000.00,'2020-06-01 01:59:26.310344');
Insert into expense values(9,'galaxy s20',2000.00,'2020-06-01 01:59:26.310344' );
Insert into expense values(10,'palm beach house',250000.00,'2020-06-01 01:59:26.310344');
Insert into expense values(11,'laptop',2550.00,'2020-06-01 01:59:26.310344');
Insert into expense values(12,'gaming laptop',3550.00,'2020-06-01 01:59:26.310344');
Insert into expense values(13,'vacation caribbean',17550.00,'2020-06-01 01:59:26.310344');
Insert into expense values(14,'vacation fiji',27550.00,'2020-06-01 01:59:26.310344');



-- -- INSERT INTO RELATIONSHIP CREATE EXPENSE
Insert into create_expense values(1,1,'2020-06-01 01:59:26.310344' );
Insert into create_expense values(1,2, '2020-06-01 01:59:26.310344');
Insert into create_expense values(2,3, '2020-06-01 01:59:26.310344');
Insert into create_expense values(3,4, '2020-06-01 01:59:26.310344');
Insert into create_expense values(4,5, '2020-06-01 01:59:26.310344');
Insert into create_expense values(5,6, '2020-06-01 01:59:26.310344');
Insert into create_expense values(6,7, '2020-06-01 01:59:26.310344');
Insert into create_expense values(7,8, '2020-06-01 01:59:26.310344');
Insert into create_expense values(8,9, '2020-06-01 01:59:26.310344');
Insert into create_expense values(9,10, '2020-06-01 01:59:26.310344');
Insert into create_expense values(10,11, '2020-06-01 01:59:26.310344');
Insert into create_expense values(10,12, '2020-06-01 01:59:26.310344');
Insert into create_expense values(11,13, '2020-06-01 01:59:26.310344');
Insert into create_expense values(12,14, '2020-06-01 01:59:26.310344');


-- -- INSERT INTO TABLE PURCHASE
Insert into purchase values(1,'BMW M3',26000.00,'2020-06-01 03:14:33.595234' );
Insert into purchase values(2,'dayton spokes',3500.00,'2020-06-01 03:14:33.595234');
Insert into purchase values(3,'Miami House',125000.00,'2020-06-01 03:14:33.595234');
Insert into purchase values(4,'Benz clk 700',36000.00,'2020-06-01 03:14:33.595234' );
Insert into purchase values(5,'sandals resort',8500.00,'2020-06-01 03:14:33.595234');
Insert into purchase values(6,'razor blade laptop',1400.00,'2020-06-01 03:14:33.595234');
Insert into purchase values(7,'asus tuf gaming',750.00,'2020-06-01 03:14:33.595234');
Insert into purchase values(8,'vehicle tires',500.00,'2020-06-01 01:59:26.310344');
Insert into purchase values(9,'galaxy s20 smart phone',1500.00,'2020-06-01 01:59:26.310344' );
Insert into purchase values(10,'palm beach house',240000.00,'2020-06-01 01:59:26.310344');
Insert into purchase values(11,'Mac book pro',2300.00,'2020-06-01 01:59:26.310344');
Insert into purchase values(12,'acer gaming laptop',1550.00,'2020-06-01 01:59:26.310344');
Insert into purchase values(13,'vacation caribbean',16550.00,'2020-06-01 01:59:26.310344');
Insert into purchase values(14,'vacation fiji',26550.00,'2020-06-01 01:59:26.310344');



-- -- INSERT INTO RELATIONSHIP CREATE PURCHASE
Insert into create_purchase values(1,1,'2020-06-01 03:14:33.595234' );
Insert into create_purchase values(2,2, '2020-06-01 03:14:33.595234');
Insert into create_purchase values(3,3, '2020-06-01 03:14:33.595234');
Insert into create_purchase values(4,4, '2020-06-01 03:14:33.595234');
Insert into create_purchase values(5,5,'2020-06-01 03:14:33.595234' );
Insert into create_purchase values(6,6, '2020-06-01 03:14:33.595234');
Insert into create_purchase values(7,7, '2020-06-01 03:14:33.595234');
Insert into create_purchase values(8,8, '2020-06-01 03:14:33.595234');
Insert into create_purchase values(9,9,'2020-06-01 03:14:33.595234' );
Insert into create_purchase values(10,10, '2020-06-01 03:14:33.595234');
Insert into create_purchase values(11,11, '2020-06-01 03:14:33.595234');
Insert into create_purchase values(12,12, '2020-06-01 03:14:33.595234');
Insert into create_purchase values(13,13, '2020-06-01 03:14:33.595234');
Insert into create_purchase values(14,14, '2020-06-01 03:14:33.595234');







-- -- STORE PROCEDURES

DELIMITER //
CREATE PROCEDURE GETUSER(IN c_id int)
BEGIN
Select* FROM user where id=c_id; 
END //
DELIMITER ;


DELIMITER //
CREATE PROCEDURE GETBUDGET(IN c_id int)
BEGIN
Select* FROM budget where id=c_id; 
END //
DELIMITER ;


DELIMITER //
CREATE PROCEDURE GETEXPENSE(IN c_id int)
BEGIN
Select* FROM expense where id=c_id; 
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GETPURCHASE(IN c_id int)
BEGIN
Select* FROM purchase where id=c_id; 
END //
DELIMITER ;



DELIMITER //
CREATE PROCEDURE GETBUDGET_DETAILS(IN c_id int)
BEGIN
Select user.id, user.email, create_budget.budget_id from user join create_budget on user.id=create_budget.user_id where create_budget.budget_id=c_id;
END //
DELIMITER ;