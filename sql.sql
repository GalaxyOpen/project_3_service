-- ai_third 
create user ai_third@localhost identified by '1234' ; -- 유저 생성
drop user ai_third@localhost; -- 유저 삭제 

create database db_ai_third; 
drop database db_ai_third;

use db_ai_third;
grant all privileges on db_ai_third.* to user_ai_third@localhost;

-- 1. 테이블 생성 (댓글 저장용) 

use db_ai_third; 

create table comments (
	id int auto_increment primary key, 
    comment_text TEXT, 
    created_at timestamp default current_timestamp
    );
    
insert into comments (comment_text)
    values('ai_third','This is generated comment.');
    
select *from comments;    