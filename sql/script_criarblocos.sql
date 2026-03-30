USE laisguer_projeto_integrador_23;


-- Remove a versão anterior para permitir a atualização sem erro 1304 
DROP PROCEDURE IF EXISTS gerar_blocos;


DELIMITER $$


CREATE PROCEDURE gerar_blocos()
BEGIN


DECLARE contador INT DEFAULT 1;
DECLARE numero_inicial INT;
DECLARE numero_final INT;


WHILE contador <= 1000 DO


    SET numero_inicial = ((contador - 1) * 10) + 1;
    SET numero_final = contador * 10;


    INSERT INTO Bloco (
        bloco_numero_inicial,
        bloco_numero_final,
        bloco_valor_numero,
        bloco_quantidade_numeros,
        bloco_valor_total
    )
    VALUES (
        numero_inicial,
        numero_final,
        100.00,
        10,
        1000.00
    );


    SET contador = contador + 1;


END WHILE;


END$$


DELIMITER ;


CALL gerar_blocos();