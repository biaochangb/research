SELECT COUNT(*) FROM lagou.`post`;
SELECT * FROM lagou.`post` WHERE job LIKE '%/%';
SELECT cname, COUNT(*) AS post_num FROM lagou.`post` GROUP BY cname ORDER BY post_num DESC INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 5.7/Uploads/company_post_num.txt';
SELECT COUNT(*) FROM lagou.`post` GROUP BY cname;
#truncate company;

SELECT cname, COUNT(*) AS post_num, `cfields`,`csize`,`cpage`,`capital`,`clocation` FROM lagou.`post` GROUP BY cname ORDER BY post_num DESC;

#提取公司信息, 并按post数量取top1000
INSERT INTO `lagou`.`company`
            ( `cname`,
             `post_num`,
             `cfields`,
             `csize`,
             `cpage`,
             `capital`,
             `clocation`)
	SELECT cname, COUNT(*) AS post_num, `cfields`,`csize`,`cpage`,`capital`,`clocation` FROM lagou.`post` GROUP BY cname ORDER BY post_num DESC;

INSERT INTO `lagou`.`company_top1000`
            ( `cname`,
             `post_num`,
             `cfields`,
             `csize`,
             `cpage`,
             `capital`,
             `clocation`)
	SELECT cname, COUNT(*) AS post_num, `cfields`,`csize`,`cpage`,`capital`,`clocation` FROM lagou.`post` GROUP BY cname ORDER BY post_num DESC LIMIT 1000;

SELECT * FROM `company_top1000` ORDER BY post_num ASC;


TRUNCATE `vocabulary`;
TRUNCATE `post_terms_top1000`;
TRUNCATE `company_terms_top1000`;









