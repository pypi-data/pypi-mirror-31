-- Represent a book
CREATE TABLE livres (
    idLivre TEXT UNIQUE,
    auteur TEXT,
    titre TEXT,
    date INTEGER
);


-- Represent all the re-usages found between two books of the corpus.
--
-- Both the source book and the dest book have theses arguments :
-- idRef: The identifier of the book
-- ordonnee: The byte where the re-use start
-- empan: Length of the re-use (in bytes)
-- texte: The re-use itself
CREATE TABLE grapheReutilisations (
    idRefSource TEXT,
    ordonneeSource INTEGER,
    empanSource INTEGER,
    texteSource TEXT,

    idRefCible TEXT,
    ordonneeCible INTEGER,
    empanCible INTEGER,
    texteCible TEXT,
    
    real_id_book_source TEXT,
    real_id_book_target TEXT
);


-- Represent all the source re-uses in the graph as well as their vertex
CREATE TABLE grapheGalaxiesSource (
    idReutilisation INTEGER UNIQUE,
    idNoeud INTEGER
);


-- Represent all the dest re-uses in the graph as well as their vertex
CREATE TABLE grapheGalaxiesCible (
    idReutilisation INTEGER UNIQUE,
    idNoeud INTEGER
);


-- Represent all the edges between two nodes of the graph
CREATE TABLE grapheGalaxies (
    idNoeudPere INTEGER,
    idNoeudFils INTEGER
);


-- Contains the number of vertices in the grap
-- TODO: Replace this table by a simple SELECT MAX(*) FROM grapheGalaxies
CREATE TABLE maxNoeud (
    idNoeud INTEGER
);


-- Contains the number of connected component in the graph
-- TODO: Replace this value (store it in a variable)
CREATE TABLE nombreGalaxies (
    nbre INTEGER
);


-- Contains info about all connected component found in the graph
-- idGalaxie: Identifier of the connected component
-- degreGalaxie: Number of vertices in the connected component
-- longueurTexteTotale: Total length of all the re-uses in the connected
--                      component
-- longueurTexteMoyenne: Mean of the length of all the re-uses in the connected
--                       component
CREATE TABLE degreGalaxies (
    idGalaxie INTEGER UNIQUE,
    degreGalaxie INTEGER,
    longueurTexteTotale INTEGER,
    longueurTexteMoyenne INTEGER
);


CREATE INDEX idLivreSource ON grapheGalaxiesSource (idNoeud);
CREATE INDEX idLivreCible ON grapheGalaxiesCible (idNoeud);
CREATE INDEX refSource ON grapheReutilisations (idRefSource);
CREATE INDEX refCible ON grapheReutilisations (idRefCible);
CREATE INDEX idNoeud ON grapheGalaxies (idNoeudPere);
CREATE INDEX idNoeudf ON grapheGalaxies (idNoeudFils);
