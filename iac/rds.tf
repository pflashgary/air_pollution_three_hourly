provider "aws" {
  region = "eu-west-1"
}

data "aws_security_group" "dm" {
  id = var.security_group_id
}

data "aws_vpc" "dm" {
  id = var.vpc_id
}

data "aws_subnets" "dm" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.dm.id]
  }
}

resource "aws_db_subnet_group" "dm" {
  name       = "dm-subnet-group"
  subnet_ids = data.aws_subnets.dm.ids
}

resource "aws_db_instance" "dm" {
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "13.3"
  instance_class       = "db.t3.micro"
  db_name              = "air_pollution"
  username             = "peggy"
  password             = "dmopenaq"
  skip_final_snapshot  = true

  vpc_security_group_ids = [data.aws_security_group.dm.id]

  db_subnet_group_name = aws_db_subnet_group.dm.name

  publicly_accessible = true

  tags = {
    Name = "dm-db"
  }

  lifecycle {
    create_before_destroy = true
  }

}