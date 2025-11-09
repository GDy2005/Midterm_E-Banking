CREATE DATABASE IF NOT EXISTS db_ebank;
USE db_ebank;

-- DROP DATABASE db_ebank;

CREATE TABLE Customer (
    CustomerID INT NOT NULL AUTO_INCREMENT,
    UserName VARCHAR(25) NOT NULL UNIQUE,
    HashPassword VARCHAR(255) NOT NULL,
    FullName VARCHAR(50) CHARACTER SET utf8mb4 NOT NULL,
    Balance INT NOT NULL DEFAULT 0,
    Email VARCHAR(50) NOT NULL,
    PhoneNumber VARCHAR(12) NOT NULL,
    
    CONSTRAINT PK_Customer PRIMARY KEY(CustomerID),
    CONSTRAINT CHK_Balance CHECK (Balance >= 0)
);

CREATE TABLE Student (
    StudentID INT NOT NULL,
    FullName VARCHAR(50) CHARACTER SET utf8mb4 NOT NULL,
    Email VARCHAR(50) NOT NULL,
    
    CONSTRAINT PK_Student PRIMARY KEY(StudentID)
);

CREATE TABLE Tution (
    TutionID INT NOT NULL AUTO_INCREMENT,
    StudentID INT NOT NULL,
    Semester VARCHAR(25) CHARACTER SET utf8mb4 NOT NULL,
    Fee INT NOT NULL DEFAULT 0,
    BeginDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    EndDate TIMESTAMP NOT NULL,
    
    CONSTRAINT PK_Tution PRIMARY KEY(TutionID),
    CONSTRAINT CHK_Fee CHECK (Fee >= 0),
    CONSTRAINT FK_Tution_Student FOREIGN KEY (StudentID) REFERENCES Student(StudentID)
);

CREATE TABLE `Transaction` (
    TransactionID INT NOT NULL AUTO_INCREMENT,
    CustomerID INT NOT NULL,
    TutionID INT NOT NULL,
    PaidAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    `Status` ENUM('PAID','UNPAID','CANCELLED') NOT NULL,
    
    CONSTRAINT PK_Transaction PRIMARY KEY(TransactionID),
    CONSTRAINT FK_Transaction_Customer FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
    CONSTRAINT FK_Transaction_Tution FOREIGN KEY (TutionID) REFERENCES Tution(TutionID)
);

-- Values 
INSERT INTO Customer (UserName, HashPassword, FullName, Balance, Email, PhoneNumber)
VALUES
('Gia Duy', 'admin123', 'Mạch Lê Gia Duy', 5000000, 'machlegiaduy2005@gmail.com', '0912345678'),
('Chi Thuan', 'admin123', 'Ngô Chí Thuận', 3000000, 'ngochithuan.dev@gmail.com', '0987654321'),
('Cao Duy', 'admin123', 'Cao Văn Duy', 100000000, 'hoa@gmail.com', '0901122334');

INSERT INTO Student (StudentID, FullName, Email)
VALUES
(1, 'Mạch Lê Gia Duy', 'machlegiaduy2005@gmail.com'),
(2, 'Tran Lan', 'ngochithuan.dev@student.com'),
(3, 'Le Hoa', 'hoa@student.com');
