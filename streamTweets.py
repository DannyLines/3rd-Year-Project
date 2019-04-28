import json
import time as time_module
import nltk
import spacy
import sqlite3
from time import mktime
from tweepy import Stream
from nltk import tokenize
from spacy import displacy
from textblob import TextBlob
from datetime import datetime
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

nlp = spacy.load('en')

Team_squads = {
"arsenal": ['Petr Cech', 'Cech', 'Hector Bellerín', 'Bellerín', 'Mohamed Elneny', 'Elneny', 'Sokratis Papastathopoulos', 'Papastathopoulos', 'Laurent Koscielny', 'Koscielny', 'Henrikh Mkhitaryan', 'Mkhitaryan', 'Aaron Ramsey', 'Ramsey', 'Alexandre Lacazette', 'Lacazette', 'Mesut Özil', 'Mesut Ozil', 'Özil', 'Ozil', 'Lucas Torreira', 'Torreira', 'Stephan Lichtsteiner', 'Lichtsteiner', 'Pierre-Emerick Aubameyang', 'Aubameyang', 'Ainsley Maitland-Niles', 'Maitland-Niles', 'Rob Holding', 'Holding', 'Alex Iwobi', 'Iwobi', 'Nacho Monreal', 'Monreal', 'Bernd Leno', 'Leno', 'Shkodran Mustafi', 'Mustafi', 'Danny Welbeck', 'Welbeck', 'Carl Jenkinson', 'Jenkinson', 'Konstantinos Mavropanos', 'Mavropanos', 'Mattéo Guendouzi', 'Guendouzi', 'Sead Kolašinac', 'Kolašinac', 'Granit Xhaka', 'Xhaka', 'Danny Ballard', 'Ballard', 'Tolaji Bola', 'Bola', 'Cohen Bramall', 'Bramall', 'Robbie Burton', 'Burton', 'Charlie Gilmour', 'Gilmour', 'Dejan Iliev', 'Iliev', 'Zech Medley', 'Medley', 'Edward Nketiah', 'Nketiah', 'Joseph Olowu', 'Olowu', 'Tobi Omole', 'Omole', 'Jordi Osei-Tutu', 'Osei-Tutu', 'Julio Pleguezuelo', 'Pleguezuelo', 'Ben Sheaf', 'Sheaf', 'Emile Smith-Rowe', 'Smith-Rowe', 'Dominic Thompson', 'Thompson', 'Nathan Tormey', 'Tormey', 'Joe Willock', 'Willock', 'Gedion Zelalem', 'Zelalem', 'Folarin Balogun', 'Balogun', 'Trae Coyle', 'Coyle', 'Tyreece John-Jules', 'John-Jules', 'James Olayinka', 'Olayinka', 'Matthew Smith', 'Smith', 'Karl Hein', 'Hein', 'Arthur Okonkwo', 'Okonkwo', 'Bukayo Saka', 'Saka'],
"bournemouth": ['Artur Boruc', 'Boruc', 'Simon Francis', 'Francis', 'Steve Cook', 'Cook', 'Dan Gosling', 'Gosling', 'Nathan Aké', 'Aké', 'Andrew Surman', 'Surman', 'Jefferson Lerma', 'Lerma', 'Lys Mousset', 'Mousset', 'Jordon Ibe', 'Ibe', 'Charlie Daniels', 'Daniels', 'Callum Wilson', 'Wilson', 'Adam Smith', 'Smith', 'Lewis Cook', 'Cook', 'Joshua King', 'King', 'Junior Stanislas', 'Stanislas', 'David Brooks', 'Brooks', 'Diego Rico', 'Rico', 'Emerson Hyndman', 'Hyndman', 'Nathaniel Clyne', 'Clyne', 'Ryan Fraser', 'Fraser', 'Jack Simpson', 'Simpson', 'Tyrone Mings', 'Mings', 'Asmir Begović', 'Begović', 'Kyle Taylor', 'Taylor', 'Dominic Solanke', 'Solanke', 'Matt Butcher', 'Butcher', 'Will Dennis', 'Dennis', 'Mark Travers', 'Travers', 'Corey Jordan', 'Jordan', 'Frank Vincent', 'Vincent', 'Charlie Seaman', 'Seaman', 'Sam Sherring', 'Sherring', 'Shaun Hobson', 'Hobson', 'Gavin Kilkenny', 'Kilkenny', 'Tyler Cordner', 'Cordner', 'Jaidon Anthony', 'Anthony', "Keelan O'Connell", "O'Connell", 'Dinesh Gillela', 'Gillela', 'Nnamdi Ofoborh', 'Ofoborh', 'James Boote', 'Boote', 'Tyrell Hamilton', 'Hamilton', 'Chris Mepham', 'Mepham'],
"brighton": ['Matthew Ryan', 'Ryan', 'Bruno Saltor', 'Saltor', 'Gaëtan Bong', 'Bong', 'Shane Duffy', 'Duffy', 'Lewis Dunk', 'Dunk', 'Dale Stephens', 'Stephens', 'Beram Kayal', 'Kayal', 'Yves Bissouma', 'Bissouma', 'Jürgen Locadia', 'Locadia', 'Florin Andone', 'Andone', 'Anthony Knockaert', 'Knockaert', 'Pascal Groß', 'Groß', 'Leon Balogun', 'Balogun', 'Alireza Jahanbakhsh', 'Jahanbakhsh', 'Glenn Murray', 'Murray', 'José Izquierdo', 'Izquierdo', 'Solly March', 'March', 'Matiás Ezequiel Schelotto', 'Ezequiel', 'Martín Montoya', 'Montoya', 'Jason Steele', 'Steele', 'Davy Pröpper', 'Pröpper', 'David Button', 'Button', 'Bernardo', 'Dan Burn', 'Burn', 'Max Sanders', 'Sanders', 'Viktor Gyökeres', 'Gyökeres', 'James Tilley', 'Tilley', 'Aaron Connolly', 'Connolly', 'Owen Moore', 'Moore', 'Archie Davies', 'Davies', 'Jordan Davies', 'Davies', "Warren O'Hora", "O'Hora", 'Josh Kerr', 'Kerr', 'Leo Østigård', 'Østigård', 'Will Collar', 'Collar', 'Peter Gwargis', 'Gwargis', 'Hugo Keto', 'Keto', 'Billy Collings', 'Collings', 'Alex Cochrane', 'Cochrane', 'Stefan Ljubičić', 'Ljubičić', 'Mathias Normann', 'Normann', 'Jack Spong', 'Spong', 'Danny Cashman', 'Cashman', 'Ryan Longman', 'Longman', 'Roco Rees', 'Rees', 'Sam Packham', 'Packham'],
"burnley": ['Thomas Heaton', 'Heaton', 'Matthew Lowton', 'Lowton', 'Charlie Taylor', 'Taylor', 'Jack Cork', 'Cork', 'James Tarkowski', 'Tarkowski', 'Ben Mee', 'Mee', 'Jóhann Guðmundsson', 'Guðmundsson', 'Sam Vokes', 'Vokes', 'Ashley Barnes', 'Barnes', 'Chris Wood', 'Wood', 'Robbie Brady', 'Brady', 'Jeff Hendrick', 'Hendrick', 'Ben Gibson', 'Gibson', 'Steven Defour', 'Defour', 'Ashley Westwood', 'Westwood', 'Jonathan Walters', 'Walters', 'Joe Hart', 'Hart', 'Anders Lindegaard', 'Lindegaard', 'Stephen Ward', 'Ward', 'Aaron Lennon', 'Lennon', 'Phillip Bardsley', 'Bardsley', 'Matěj Vydra', 'Vydra', 'Kevin Long', 'Long', 'Nick Pope', 'Pope', 'Adam Legzdins', 'Legzdins', 'Dwight McNeil', 'McNeil', 'Daniel Agyei', 'Agyei', 'Oliver Younger', 'Younger', 'Josh Benson', 'Benson'],
"cardiff": ['Neil Etheridge', 'Etheridge', 'Lee Peltier', 'Peltier', 'Joe Bennett', 'Bennett', 'Sean Morrison', 'Morrison', 'Bruno Ecuele Manga', 'Ecuele', 'Ashley Richards', 'Richards', 'Harry Arter', 'Arter', 'Joe Ralls', 'Ralls', 'Danny Ward', 'Ward', 'Kenneth Zohore', 'Zohore', 'Josh Murphy', 'Murphy', 'Alex Smithies', 'Smithies', 'Callum Paterson', 'Paterson', 'Bobby Reid', 'Reid', 'Matthew Connolly', 'Connolly', 'Aron Gunnarsson', 'Gunnarsson', 'Greg Cunningham', 'Cunningham', 'Nathaniel Mendez-Laing', 'Mendez-Laing', 'Loïc Damour', 'Damour', 'Víctor Camarasa', 'Camarasa', 'Souleymane Bamba', 'Bamba', 'Kadeem Harris', 'Harris', '\n', 'Brian Murphy', 'Murphy', 'Oumar Niasse', 'Niasse', 'Rhys Healey', 'Healey', 'Junior Hoilett', 'Hoilett', 'James Waite', 'Waite', 'Cameron Coxe', 'Coxe', 'Ciaron Brown', 'Brown', 'Lloyd Humphries', 'Humphries', 'Emiliano Sala', 'Sala'],
"chelsea": ['Kepa Arrizabalaga', 'Arrizabalaga', 'Antonio Rüdiger', 'Rüdiger', 'Marcos Alonso', 'Alonso', 'Jorginho', 'Danny Drinkwater', 'Drinkwater', 'Ngolo Kanté', 'Kanté', 'Ross Barkley', 'Barkley', 'Gonzalo Higuaín', 'Higuaín', 'Eden Hazard', 'Hazard', 'Pedro', 'Ruben Loftus-Cheek', 'Loftus-Cheek', 'Wilfredo Caballero', 'Caballero', 'Victor Moses', 'Moses', 'Mateo Kovačić', 'Kovačić', 'Olivier Giroud', 'Giroud', 'Callum Hudson-Odoi', 'Hudson-Odoi', 'Davide Zappacosta', 'Zappacosta', 'Willian', 'Gary Cahill', 'Cahill', 'Andreas Christensen', 'Christensen', 'César Azpilicueta', 'Azpilicueta', 'Álvaro Morata', 'Morata', 'David Luiz', 'Luiz', 'Robert Green', 'Green', 'Emerson Palmieri', 'Palmieri', 'Iké Ugbo', 'Ugbo', 'Ethan Ampadu', 'Ampadu', 'Joseph Colley', 'Colley', 'Richard Nartey', 'Nartey', 'Luke McCormick', 'McCormick', 'Charlie Brown', 'Brown', 'Conor Gallagher', 'Gallagher', 'Jamie Cumming', 'Cumming', 'Marc Guehi', 'Guehi', 'Juan Castillo', 'Castillo', 'George McEachran', 'McEachran', 'Martell Taylor-Crossdale', 'Taylor-Crossdale', 'Tariq Uwakwe', 'Uwakwe', 'Daishawn Redan', 'Redan', 'Marcin Bułka', 'Bułka', 'Billy Gilmour', 'Gilmour', 'Tariq Lamptey', 'Lamptey', 'Marcel Lavinier', 'Lavinier', 'Faustino Anjorin', 'Anjorin', 'Renedi Masampu', 'Masampu', 'Nicolas Tie', 'Tie', 'Ian Maatsen', 'Maatsen', 'Jared Thompson', 'Thompson', 'Clinton Mola', 'Mola'],
"crystal palace": ['Julián Speroni', 'Speroni', 'Joel Ward', 'Ward', 'Patrick van Aanholt', 'van', 'Luka Milivojević', 'Milivojević', 'James Tomkins', 'Tomkins', 'Scott Dann', 'Dann', 'Max Meyer', 'Meyer', 'Cheikhou Kouyaté', 'Kouyaté', 'Andros Townsend', 'Townsend', 'Wilfried Zaha', 'Zaha', 'Mamadou Sakho', 'Sakho', 'Wayne Hennessey', 'Hennessey', 'Jordan Ayew', 'Ayew', 'Jeffrey Schlupp', 'Schlupp', 'Christian Benteke', 'Benteke', 'James McArthur', 'McArthur', 'Connor Wickham', 'Wickham', 'Sullay Kaikai', 'Kaikai', "Pape N'Diaye Souaré", "N'Diaye", 'Aaron Wan-Bissaka', 'Wan-Bissaka', 'Dion Henry', 'Henry', 'Vicente Guaita', 'Guaita', 'Martin Kelly', 'Kelly', 'Sam Woods', 'Woods', 'Gio McGregor', 'McGregor', 'Kian Flanagan', 'Flanagan', 'Tyrick Mitchell', 'Mitchell', 'Joe Tupper', 'Tupper', 'Jaïro Riedewald', 'Riedewald'],
"everton": ['Jordan Pickford', 'Pickford', 'Leighton Baines', 'Baines', 'Michael Keane', 'Keane', 'Kurt Zouma', 'Zouma', 'Phil Jagielka', 'Jagielka', 'André Gomes', 'Gomes', 'Gylfi Sigurðsson', 'Sigurðsson', 'Theo Walcott', 'Walcott', 'Lucas Digne', 'Digne', 'Yerry Mina', 'Mina', 'Cenk Tosun', 'Tosun', 'James McCarthy', 'McCarthy', 'Idrissa Gueye', 'Gueye', 'Morgan Schneiderlin', 'Schneiderlin', 'Bernard', 'Maarten Stekelenburg', 'Stekelenburg', 'Séamus Coleman', 'Coleman', 'Tom Davies', 'Davies', 'Dominic Calvert-Lewin', 'Calvert-Lewin', 'Richarlison', 'Ademola Lookman', 'Lookman', 'João Virgínia', 'Virgínia', 'Beni Baningime', 'Baningime', 'Tyias Browning', 'Browning', 'Brendan Galloway', 'Galloway', 'Harry Charsley', 'Charsley', 'Matty Foulds', 'Foulds', 'Dennis Adeniran', 'Adeniran', 'Mateusz Hewelto', 'Hewelto', 'Josh Bowler', 'Bowler', 'Jonjoe Kenny', 'Kenny', 'Bassala Sambou', 'Sambou', 'Fraser Hornby', 'Hornby', 'Morgan Feeney', 'Feeney', 'Antony Evans', 'Evans', 'Nathan Broadhead', 'Broadhead', 'Chris Renshaw', 'Renshaw', 'Lewis Gibson', 'Gibson', 'Nathangelo Markelo', 'Markelo', 'Anthony Gordon', 'Gordon', 'Boris Mathis', 'Mathis', 'Alex Denny', 'Denny', 'Daniel Bramall', 'Bramall', 'Shayne Lavery', 'Lavery', 'Jack Kiersey', 'Kiersey', 'Joe Hilton', 'Hilton', 'Con Ouzounidis', 'Ouzounidis', 'Manasse Mampala', 'Mampala', 'Nicolas Hansen', 'Hansen', 'Ryan Astley', 'Astley', 'Kyle John', 'John', 'Kieran Phillips', 'Phillips', 'Ellis Simms', 'Simms'],
"fulham": ['Marcus Bettinelli', 'Bettinelli', 'Ryan Sessegnon', 'Sessegnon', 'Denis Odoi', 'Odoi', 'Calum Chambers', 'Chambers', 'Kevin McDonald', 'McDonald', 'Neeskens Kebano', 'Kebano', 'Stefan Johansen', 'Johansen', 'Aleksandar Mitrović', 'Mitrović', 'Tom Cairney', 'Cairney', 'Floyd Ayité', 'Ayité', 'Ryan Babel', 'Babel', 'Tim Ream', 'Ream', 'Andre Schürrle', 'Schürrle', 'Rui Fonte', 'Fonte', 'Luciano Vietto', 'Vietto', 'Maxime Le Marchand', 'Le', 'Timothy Fosu-Mensah', 'Fosu-Mensah', 'Cyrus Christie', 'Christie', 'Joe Bryan', 'Bryan', 'Jean Michaël Seri', 'Michaël', 'Sergio Rico', 'Rico', 'Alfie Mawson', 'Mawson', 'André-Frank Zambo Anguissa', 'Zambo', 'Fabricio', "Matt O'Riley", "O'Riley", 'Jerome Opoku', 'Opoku', 'Moritz Jenz', 'Jenz', 'Luca De La Torre', 'De', 'Jón Dagur Þorsteinsson', 'Dagur', 'Tyrese Francois', 'Francois', 'Toni Stahl', 'Stahl', 'Cameron Thompson', 'Thompson', 'Jaydn Mundle-Smith', 'Mundle-Smith', 'Jayden Harris', 'Harris', 'Steven Sessegnon', 'Sessegnon', 'Ibrahima Cissé', 'Cissé', 'José Garrido', 'Garrido', 'Chris Kelly', 'Kelly', 'Aboubakar Kamara', 'Kamara', 'Sonny Hilton', 'Hilton', 'Ben Davies', 'Davies', 'Luca Ashby-Hammond', 'Ashby-Hammond', 'Timmy Abraham', 'Abraham', 'Zico Asare', 'Asare', 'George Wickens', 'Wickens', 'Cody Drameh', 'Drameh', 'Sylvester Jasper', 'Jasper', 'Harvey Elliott', 'Elliott', 'Aron Davies', 'Davies', 'Jean-Pierre Tiehi', 'Tiehi', 'Fabio Carvalho', 'Carvalho', 'Taye Ashby-Hammond', 'Ashby-Hammond', 'Nicolás Santos', 'Santos'],
"huddersfield": ['Jonas Lossl', 'Lossl', 'Tommy Smith', 'Smith', 'Terence Kongolo', 'Kongolo', 'Jonathan Hogg', 'Hogg', 'Juninho Bacuna', 'Bacuna', 'Philip Billing', 'Billing', 'Elias Kachunga', 'Kachunga', 'Aaron Mooy', 'Mooy', 'Adama Diakhaby', 'Diakhaby', 'Ben Hamer', 'Hamer', 'Ramadan Sobhi', 'Sobhi', 'Chris Löwe', 'Löwe', 'Isaac Mbenza', 'Mbenza', 'Daniel Williams', 'Williams', 'Laurent Depoitre', 'Depoitre', 'Alex Pritchard', 'Pritchard', 'Steve Mounié', 'Mounié', 'Mathias Zanka Jørgensen', 'Zanka', 'Christopher Schindler', 'Schindler', 'Jon Gorenc Stanković', 'Gorenc', 'Abdelhamid Sabiri', 'Sabiri', 'Florent Hadergjonaj', 'Hadergjonaj', 'Eric Durm', 'Durm', 'Matty Daly', 'Daly', 'Jason Puncheon', 'Puncheon'],
"leicester": ['Kasper Schmeichel', 'Schmeichel', 'Danny Simpson', 'Simpson', 'Ben Chilwell', 'Chilwell', 'Çağlar Söyüncü', 'Söyüncü', 'Wes Morgan', 'Morgan', 'Jonny Evans', 'Evans', 'Demarai Gray', 'Gray', 'Kelechi Iheanacho', 'Iheanacho', 'Jamie Vardy', 'Vardy', 'James Maddison', 'Maddison', 'Marc Albrighton', 'Albrighton', 'Danny Ward', 'Ward', 'Ricardo Pereira', 'Pereira', 'Harry Maguire', 'Maguire', 'Eldin Jakupović', 'Jakupović', 'Daniel Amartey', 'Amartey', 'Harvey Barnes', 'Barnes', 'Shinji Okazaki', 'Okazaki', 'Matthew James', 'James', 'Adrien Silva', 'Silva', 'Nampalys Mendy', 'Mendy', 'Wilfred Ndidi', 'Ndidi', 'Christian Fuchs', 'Fuchs', 'Layton Ndukwu', 'Ndukwu', 'Rachid Ghezzal', 'Ghezzal', 'Bartosz Kapustka', 'Kapustka', 'Josh Knight', 'Knight', 'Admiral Muskwe', 'Muskwe', 'Andy King', 'King', 'Hamza Choudhury', 'Choudhury', 'Darnell Johnson', 'Johnson', 'Viktor Johansson', 'Johansson', 'Max Bramley', 'Bramley', 'Rhys Davies', 'Davies', 'Jakub Stolarczyk', 'Stolarczyk', 'Sam Hughes', 'Hughes', 'Callum Wright', 'Wright', 'Josh Eppiah', 'Eppiah', 'Lamine Sherif', 'Sherif', 'Kieran Dewsbury-Hall', 'Dewsbury-Hall', 'Alex Pașcanu', 'Pașcanu', 'Liandro Martis', 'Martis', 'Ryan Loft', 'Loft', 'Louis Ramsay', 'Ramsay', 'Raúl Uche', 'Uche', 'Tyrese Shade', 'Shade', 'Kairo Edwards-John', 'Edwards-John', 'George Heaven', 'Heaven', 'Conor Tee', 'Tee', 'Khanya Leshbela', 'Leshbela', 'Calvin Ughelumba', 'Ughelumba', 'Ed Elewa-Ikpakwu', 'Elewa-Ikpakwu', 'Luke Thomas', 'Thomas', 'Dennis Gyamfi', 'Gyamfi', 'Lukáš Husek', 'Husek', 'Sidnei Tavares', 'Tavares', 'Will Russ', 'Russ'],
"liverpool": ['Fabinho', 'Virgil van Dijk', 'van', 'Georginio Wijnaldum', 'Wijnaldum', 'Dejan Lovren', 'Lovren', 'James Milner', 'Milner', 'Naby Keïta', 'Keïta', 'Roberto Firmino', 'Firmino', 'Sadio Mané', 'Mané', 'Mohamed Salah', 'Salah', 'Joe Gomez', 'Gomez', 'Alisson Becker', 'Becker', 'Jordan Henderson', 'Henderson', 'Daniel Sturridge', 'Sturridge', 'Alberto Moreno', 'Moreno', 'Adam Lallana', 'Lallana', 'Alex Oxlade-Chamberlain', 'Oxlade-Chamberlain', 'Simon Mignolet', 'Mignolet', 'Xherdan Shaqiri', 'Shaqiri', 'Rhian Brewster', 'Brewster', 'Andrew Robertson', 'Robertson', 'Divock Origi', 'Origi', 'Joel Matip', 'Matip', 'Nathaniel Phillips', 'Phillips', 'Curtis Jones', 'Jones', 'George Johnston', 'Johnston', 'Lazar Marković', 'Marković', 'Ki-Jana Hoever', 'Hoever', 'Isaac Christie-Davies', 'Christie-Davies', 'Caoimhin Kelleher', 'Kelleher', 'Conor Masterson', 'Masterson', 'Rafael Camacho', 'Camacho', 'Trent Alexander-Arnold', 'Alexander-Arnold', 'Pedro Chirivella', 'Chirivella'],
"man city": ['Claudio Bravo', 'Bravo', 'Kyle Walker', 'Walker', 'Danilo', 'Vincent Kompany', 'Kompany', 'John Stones', 'Stones', 'Raheem Sterling', 'Sterling', 'İlkay Gündoğan', 'Gündoğan', 'Sergio Agüero', 'Agüero', 'Aymeric Laporte', 'Laporte', 'Eliaquim Mangala', 'Mangala', 'Kevin De Bruyne', 'De', 'Fabian Delph', 'Delph', 'Leroy Sané', 'Sané', 'Bernardo Silva', 'Silva', 'David Silva', 'Silva', 'Benjamin Mendy', 'Mendy', 'Fernandinho', 'Riyad Mahrez', 'Mahrez', 'Nicolás Otamendi', 'Otamendi', 'Ederson', 'Daniel Grimshaw', 'Grimshaw', 'Gabriel Jesus', 'Jesus', 'Philippe Sandler', 'Sandler', 'Oleksandr Zinchenko', 'Zinchenko', 'Phil Foden', 'Foden', 'Arijanet Murić', 'Murić', 'Eric García', 'García', 'Nabil Touaizi', 'Touaizi', 'Felix Nmecha', 'Nmecha', 'Joel Latibeaudiere', 'Latibeaudiere', 'Iker Pozo', 'Pozo', 'Tommy Doyle', 'Doyle', 'Jayden Braaf', 'Braaf', 'Jeremie Frimpong', 'Frimpong', 'Tom Dele-Bashiru', 'Dele-Bashiru', 'Benjamín Garré', 'Garré', 'Luke Bolton', 'Bolton', 'Cameron Humphreys', 'Humphreys', 'Taylor Harwood-Bellis', 'Harwood-Bellis', 'Lorenzo González', 'González', 'Claudio Gomes', 'Gomes', 'Adrián Bernabé', 'Bernabé', 'Ian Carlo Poveda', 'Carlo', 'Rabbi Matondo', 'Matondo', 'Colin Rösler', 'Rösler', 'Curtis Anderson', 'Anderson', 'Thomas Scott', 'Scott', 'Richard Dionkou', 'Dionkou', 'Taylor Richards', 'Richards', 'Tyreke Wilson', 'Wilson', 'Nathaniel Ogbeta', 'Ogbeta', 'Henri Ogunby', 'Ogunby', 'Keyendrah Simmonds', 'Simmonds', 'Louie Moulden', 'Moulden', 'Lewis Fiorini', 'Fiorini', 'Ben Knight', 'Knight', 'Rowan McDonald', 'McDonald'],
"man utd": ['David De Gea', 'De', 'Victor  Lindelöf', '', 'Eric Bailly', 'Bailly', 'Phil Jones', 'Jones', 'Paul Pogba', 'Pogba', 'Alexis Sánchez', 'Sánchez', 'Juan Mata', 'Mata', 'Romelu Lukaku', 'Lukaku', 'Marcus Rashford', 'Rashford', 'Anthony Martial', 'Martial', 'Chris Smalling', 'Smalling', 'Lee Grant', 'Grant', 'Jesse Lingard', 'Lingard', 'Andreas Pereira', 'Pereira', 'Marcos Rojo', 'Rojo', 'Fred', 'Ashley Young', 'Young', 'Diogo Dalot', 'Dalot', 'Ander Herrera', 'Herrera', 'Sergio Romero', 'Romero', 'Luke Shaw', 'Shaw', 'Luis Antonio Valencia', 'Antonio', 'Marouane Fellaini', 'Fellaini', 'Nemanja Matić', 'Matić', 'Matteo Darmian', 'Darmian', 'James Garner', 'Garner', 'Scott McTominay', 'McTominay', 'Joel  Pereira', '', 'Matty Willock', 'Willock', 'Tahith Chong', 'Chong', 'Joshua Bohui', 'Bohui', 'Angel Gomes', 'Gomes', 'Matěj Kovář', 'Kovář', 'Mason Greenwood', 'Greenwood'],
"newcastle": ['Robert Elliot', 'Elliot', 'Ciaran Clark', 'Clark', 'Paul Dummett', 'Dummett', 'Ki Sung-Yueng', 'Sung-Yueng', 'Fabian Schär', 'Schär', 'Jamaal Lascelles', 'Lascelles', 'Jacob Murphy', 'Murphy', 'Jonjo Shelvey', 'Shelvey', 'José Salomón Rondón', 'Salomón', 'Mohamed Diamé', 'Diamé', 'Matt Ritchie', 'Ritchie', 'Martin Dúbravka', 'Dúbravka', 'Yoshinori Mutō', 'Mutō', 'Isaac Hayden', 'Hayden', 'Kenedy', 'Ayoze Pérez', 'Pérez', 'Federico Fernández', 'Fernández', 'Javi Manquillo', 'Manquillo', 'Florian Lejeune', 'Lejeune', 'Joselu', 'DeAndre Yedlin', 'Yedlin', 'Jamie Sterry', 'Sterry', 'Karl Darlow', 'Darlow', 'Nathan Harker', 'Harker', 'Christian Atsu', 'Atsu', 'Otto Huuhtanen', 'Huuhtanen', 'Sean Longstaff', 'Longstaff', 'Callum Roberts', 'Roberts', 'Stefan O’Connor', 'O’Connor', 'Rosaire Longelo', 'Longelo', 'Freddie Woodman', 'Woodman', 'Mohammed Sangare', 'Sangare', 'Matthew Longstaff', 'Longstaff', 'Lewis Cass', 'Cass', 'Owen Bailey', 'Bailey', 'Kelland Watts', 'Watts', 'Tom Allan', 'Allan', 'Yannick Toure', 'Toure', 'Achraf Lazaar', 'Lazaar', 'Juanito', 'Oliver Walters', 'Walters', 'Adam Wilson', 'Wilson', 'Dan Langley', 'Langley', 'Oisin McEntee', 'McEntee'],
"southampton": ['Alex McCarthy', 'McCarthy', 'Cédric Soares', 'Soares', 'Maya Yoshida', 'Yoshida', 'Jannik Vestergaard', 'Vestergaard', 'Jack Stephens', 'Stephens', 'Shane Long', 'Long', 'Danny Ings', 'Ings', 'Charlie Austin', 'Austin', 'Mohamed Elyounoussi', 'Elyounoussi', 'Oriol Romeu', 'Romeu', 'Sam Gallagher', 'Gallagher', 'James Ward-Prowse', 'Ward-Prowse', 'Stuart Armstrong', 'Armstrong', 'Mario Lemina', 'Lemina', 'Ryan Bertrand', 'Bertrand', 'Nathan Redmond', 'Redmond', 'Pierre-Emile Højbjerg', 'Højbjerg', 'Angus Gunn', 'Gunn', 'Alfie Jones', 'Jones', 'Matt Targett', 'Targett', 'Jan Bednarek', 'Bednarek', 'Josh Sims', 'Sims', 'Harry Lewis', 'Lewis', 'Yan Valery', 'Valery', 'Fraser Forster', 'Forster', 'Will Ferry', 'Ferry', 'Kornelius Hansen', 'Hansen', "Thomas O'Connor", "O'Connor", 'Ben Rowthorn', 'Rowthorn', 'Tyreke Johnson', 'Johnson', "Dan N'Lundulu", "N'Lundulu", 'Christoph Klarer', 'Klarer', 'Callum Slattery', 'Slattery', 'Adam Parkes', 'Parkes', 'Jake Vokins', 'Vokins', "Aaron O'Driscoll", "O'Driscoll", 'Jonathan Afolabi', 'Afolabi', 'Will Smallbone', 'Smallbone', 'Michael Obafemi', 'Obafemi', 'Jack Rose', 'Rose', 'Harrison Davis', 'Davis', 'Nathan Tella', 'Tella', 'Marcus Barnes', 'Barnes', 'Kayne Ramsay', 'Ramsay', 'Alex Cull', 'Cull', 'Harlem Hale', 'Hale', 'Enzo Robise', 'Robise', 'Harry Hamblin', 'Hamblin', 'Jamie Bradley-Green', 'Bradley-Green', 'Siphesile Mdlalose', 'Mdlalose', 'Alex Jankewitz', 'Jankewitz', 'Christian Norton', 'Norton', 'Allan Tchaptchet', 'Tchaptchet'],
"tottenham": ['Hugo Lloris', 'Lloris', 'Kieran Trippier', 'Trippier', 'Danny Rose', 'Rose', 'Toby Alderweireld', 'Alderweireld', 'Jan Vertonghen', 'Vertonghen', 'Davinson Sánchez', 'Sánchez', 'Son Heung-Min', 'Heung-Min', 'Harry Winks', 'Winks', 'Harry Kane', 'Kane', 'Erik Lamela', 'Lamela', 'Victor Wanyama', 'Wanyama', 'Michel Vorm', 'Vorm', 'Georges-Kevin Nkoudou', 'Nkoudou', 'Eric Dier', 'Dier', 'Kyle Walker-Peters', 'Walker-Peters', 'Moussa Sissoko', 'Sissoko', 'Fernando Llorente', 'Llorente', 'Mousa Dembélé', 'Dembélé', 'Dele Alli', 'Alli', 'Juan Foyth', 'Foyth', 'Paulo Gazzaniga', 'Gazzaniga', 'Christian Eriksen', 'Eriksen', 'Serge Aurier', 'Aurier', 'Lucas', 'Ben Davies', 'Davies', 'Shayon Harrison', 'Harrison', 'Luke Amos', 'Amos', 'Alfie Whiteman', 'Whiteman', 'Anthony Georgiou', 'Georgiou', 'Tashan Oakley-Boothe', 'Oakley-Boothe', 'George Marsh', 'Marsh', 'Jonathan Dinzeyi', 'Dinzeyi', 'Brandon Austin', 'Austin', 'Kazaiah Sterling', 'Sterling', 'Shilow Tracey', 'Tracey', 'Oliver Skipp', 'Skipp', 'Timothy Eyoma', 'Eyoma', 'Dylan Duncan', 'Duncan', 'Jack Roles', 'Roles', 'Japhet Tanganga', 'Tanganga', 'Jamie Reynolds', 'Reynolds', 'Jonathan De Bie', 'De', 'Tariq Hinds', 'Hinds', 'Jamie Bowden', 'Bowden', 'Brooklyn Lyons-Foster', 'Lyons-Foster', 'Paris Maghoma', 'Maghoma', 'Dilan Markanday', 'Markanday', 'Phoenix Patterson', 'Patterson', 'Armando Shashoua', 'Shashoua', "J'Neil Bennett", 'Bennett', 'Malachi Walcott', 'Walcott', 'Troy Parrott', 'Parrott', 'Harvey White', 'White', 'Luis Binks', 'Binks', 'Tom Glover', 'Glover', 'Rodel Richards', 'Richards', 'Rayan Clarke', 'Clarke', 'Elliot Thorpe', 'Thorpe', 'Chay Cooper', 'Cooper', 'Jubril Okedina', 'Okedina'],
"watford": ['Heurelho Gomes', 'Gomes', 'Daryl Janmaat', 'Janmaat', 'Miguel Angel Britos', 'Angel', 'Sebastian Prödl', 'Prödl', 'Adrian Mariappa', 'Mariappa', 'Gerard Deulofeu', 'Deulofeu', 'Tom Cleverley', 'Cleverley', 'Troy Deeney', 'Deeney', 'Isaac Success', 'Success', 'Adam Masina', 'Masina', 'Ken Sema', 'Sema', 'Nathaniel Chalobah', 'Chalobah', 'Craig Cathcart', 'Cathcart', 'Abdoulaye Doucouré', 'Doucouré', 'Adalberto Peñaranda', 'Peñaranda', 'Andre Gray', 'Gray', 'Will Hughes', 'Hughes', 'Domingos Quina', 'Quina', 'Kiko Femenía', 'Femenía', 'Marc Navarro', 'Navarro', 'Ben Wilmot', 'Wilmot', 'José Holebas', 'Holebas', 'Ben Foster', 'Foster', 'Christian Kabasele', 'Kabasele', 'Étienne Capoue', 'Capoue', 'Pontus Dahlberg', 'Dahlberg', 'Roberto Pereyra', 'Pereyra'],
"west-ham": ['Łukasz Fabiański', 'Fabiański', 'Winston Reid', 'Reid', 'Aaron Cresswell', 'Cresswell', 'Fabián Balbuena', 'Balbuena', 'Pablo Zabaleta', 'Zabaleta', 'Marko Arnautović', 'Arnautović', 'Felipe Anderson', 'Anderson', 'Andy Carroll', 'Carroll', 'Manuel Lanzini', 'Lanzini', 'Robert Snodgrass', 'Snodgrass', 'Adrián', 'Pedro  Obiang', '', 'Carlos Sánchez', 'Sánchez', 'Mark Noble', 'Noble', 'Javier Hernández', 'Hernández', 'Samir Nasri', 'Nasri', 'Jack Wilshere', 'Wilshere', 'Andriy Yarmolenko', 'Yarmolenko', 'Angelo Ogbonna', 'Ogbonna', 'Issa Diop', 'Diop', 'Ryan Fredericks', 'Fredericks', 'Arthur Masuaku', 'Masuaku', 'Lucas', 'Michail Antonio', 'Antonio', 'Xande Silva', 'Silva', 'Nathan Trott', 'Trott', 'Reece Oxford', 'Oxford', 'Nathan Holland', 'Holland', 'Josh Pask', 'Pask', 'Declan Rice', 'Rice', 'Grady Diangana', 'Diangana', 'Jahmal Hector-Ingram', 'Hector-Ingram', 'Dan Kemp', 'Kemp', 'Joseph Anang', 'Anang', 'Anthony Scully', 'Scully', 'Tunji Akinola', 'Akinola', 'Ben Johnson', 'Johnson', 'Conor Coventry', 'Coventry', 'Alfie Lewis', 'Lewis', 'Ajibola Alese', 'Alese', 'Bernardo Rosa', 'Rosa', 'Jay Mingi', 'Mingi', 'Mason Barrett', 'Barrett', 'Emmanuel Longelo', 'Longelo', 'Jeremy Ngakia', 'Ngakia', 'Kristijan Belić', 'Belić', 'Daniel Jinadu', 'Jinadu', 'Sean Adarkwa', 'Adarkwa', 'Veron Parkes', 'Parkes', 'Peter Stroud', 'Stroud', 'Sebastian Nebyla', 'Nebyla', 'Odysseas Spyrides', 'Spyrides', 'Joshua Okotcha', 'Okotcha', 'Reece Hannam', 'Hannam', 'Daniel Chesters', 'Chesters'],
"wolves": ['Matt Doherty', 'Doherty', 'Ryan Bennett', 'Bennett', 'Ivan Cavaleiro', 'Cavaleiro', 'Rubén Neves', 'Neves', 'Raúl Jiménez', 'Jiménez', 'Hélder Costa', 'Costa', 'Rui Patrício', 'Patrício', 'Willy Boly', 'Boly', 'Conor Coady', 'Coady', 'Morgan Gibbs-White', 'Gibbs-White', 'Diogo Jota', 'Jota', 'Jonny', 'John Ruddy', 'Ruddy', 'Ryan John Giles', 'John', 'Benny Ashley-Seal', 'Ashley-Seal', 'Elliot Watt', 'Watt', 'Pedro Gonçalves', 'Gonçalves', 'Romain Saïss', 'Saïss', 'João Moutinho', 'Moutinho', 'Rúben Vinagre', 'Vinagre', 'Will Norris', 'Norris', 'Leander Dendoncker', 'Dendoncker', 'Léo Bonatini', 'Bonatini', 'Adama Traoré', 'Traoré', 'Paulinho', 'Harry Beasley', 'Beasley', 'Oskar Buur', 'Buur', 'Aaron Crabtree', 'Crabtree', 'Daniel Csóka', 'Csóka', 'Sadou Diallo', 'Diallo', 'João Caiado', 'Caiado', 'Niall Ennis', 'Ennis', 'Carlos Heredia', 'Heredia', 'Cameron John', 'John', 'Connor Johnson', 'Johnson', 'Max Kilman', 'Kilman', 'John Kitolano', 'Kitolano', 'Diego Lattie', 'Lattie', 'Dan McKenna', 'McKenna', 'Alexander Molberg', 'Molberg', 'Owen Otasowie', 'Otasowie', 'Taylor Perry', 'Perry', 'Connor Ronan', 'Ronan', 'Jack Ruddy', 'Ruddy', 'Austin Samuels', 'Samuels', 'Dion Sanderson', 'Sanderson', 'Enzo Sauvage', 'Sauvage', 'Andrew Sealey-Harris', 'Sealey-Harris', 'Andreas Søndergaard', 'Søndergaard', 'Terry Taylor', 'Taylor', "Ray O'Sullivan", "O'Sullivan", 'Callum Thompson', 'Thompson', 'Lewis Richards', 'Richards', 'Dominic Iorfa', 'Iorfa', 'Luke Cundle', 'Cundle', 'Todd Parker', 'Parker'],
}

Team_abbreviations = {
    "liverpool": "LIV",
    "man city": "MCI",
    "tottenham": "TOT",
    "chelsea": "CHE",
    "arsenal": "ARS",
    "man utd": "MUN",
    "leicester": "LEI",
    "west ham": "WHU",
    "watford": "WAT",
    "wolves": "WOL",
    "everton": "EVE",
    "bournemouth": "BOU",
    "brighton": "BRI",
    "crystal palace": "CRY",
    "newcastle": "NEW",
    "burnley": "BUR",
    "cardiff city": "CAR",
    "southampton": "SOU",
    "fulham": "FUL",
    "huddersfield": "HUD"
}

Team_identifiers = {
    "liverpool": ["LFC", "liverpool", "reds"],
    "man city": ["MCFC", "man city", "manchester city", "city"],
    "tottenham": ["THFC", "tottenham", "spurs"],
    "chelsea": ["CFC", "chels", "chelsea", "blues"],
    "arsenal": ["AFC", "arsenal", "gunners", "ars"],
    "man utd": ["MUFC", "red devils", "manchester united", "man u", "man utd", "man united", "devils", "united", "utd"],
    "leicester": ["LCFC", "leicester", "leicester city", "foxes"],
    "west ham": ["WHFC", "irons", "hammers", "west ham"],
    "watford": ["WFC", "watford fc", "watford"],
    "wolves": ["WWFC", "wolves", "wolverhampton wanderers"],
    "everton": ["EVE", "everton", "everton fc", "toffees"],
    "bournemouth": ["BOU", "BHA", "bournemouth", "bournemouth fc", "cherries"],
    "brighton": ["BRI", "brighton fc", "brighton", "seagulls"],
    "crystal palace": ["CRY", "crystal palace", "palace", "eagles"],
    "newcastle": ["NEW", "newcastle", "newcastle united fc", "castle"],
    "burnley": ["BUR", "clarets", "burnley"],
    "cardiff city": ["CAR", "bluebirds", "cardiff city", "cardiff"],
    "southampton": ["SOU", "southampton", "saints", "southampton fc"],
    "fulham": ["FUL", "fulham", "fulham fc"],
    "huddersfield": ["HUD", "huddersfield, terriers"]
}

# TODO
# Identify Subject of Sentence
#
# Identify Object of Sentence
#
# Store Tweeter details
#
# Compare tweet to average response of other users
# If tweeter consistently out of std var of average response then this
# users response is often useless and should blacklist this user so the tweets
# are ignored
#
# Identify sarcasm by extreme outlier shifted to opposite polarity
# I.e. extremely positive tweet when overall average sentiment is very negative for the given team
#
# What if subject is a player of a given team? Need list of players for each team and these tweets to be considered

ACCESS_TOKEN = "2460921473-QkIBOaOI0AQjtbqovO88IA2T5ATOI0h1vUYKRts"
ACCESS_TOKEN_SECRET = "ZWNGkGLhb91rmVH1RENkgPVq9C6R4AZfKxcXSdMJJAllb"
CONSUMER_KEY = "CCDd0CvDC3g4a1kyopo48lCwG"
CONSUMER_SECRET = "Ajysc67bUC8cM3tp8Ox1IlthqE7irXRTTG5rxpirjabSKKmDeK"
current_match_time = 0

class TwitterStreamer():
    def stream_tweets(selfself, hashtag_list):
        listener = StdOutListener()
        auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

        stream = Stream(auth, listener, tweet_mode='extended')

        stream.filter(track=hashtag_list)

# Need to consider "This man-utd side" as this becomes subject I think
# Get original tweet of retweets
class StdOutListener(StreamListener):

    def on_data(self, data):
        #print("Tweet received!")
        try:
            home_team_synonyms = Team_identifiers[HOME_TEAM] + Team_squads[HOME_TEAM]
            away_team_synonyms = Team_identifiers[AWAY_TEAM] + Team_squads[AWAY_TEAM]
            home_team_synonyms = [x.lower() for x in home_team_synonyms]
            away_team_synonyms = [x.lower() for x in away_team_synonyms]
            newData = json.loads(data)
            looping = True
            try:
                analysis = str(TextBlob(newData["extended_tweet"]["full_text"]))
            except:
                analysis = str(TextBlob(newData["text"]))
            analysis = nlp(analysis)
            sentences = list(analysis.sents)
            tweet_about = 0

            for sentence in sentences:
                root_token = sentence.root
                for child in root_token.children:
                    if child.dep_ == 'nsubj':
                        subject = str(child).lower()
                        if subject in home_team_synonyms:
                            tweet_about = 1
                        elif subject in away_team_synonyms:
                            tweet_about = 2
                        if tweet_about != 0:
                            try:
                                cursor2.execute("select time from " + match_time_table + " order by id desc")
                                rows = cursor2.fetchall()
                            except Exception as e:
                                print(e)

                            for row in rows:
                                for entry in row:
                                    current_match_time = entry
                                break
                            sentence_text = TextBlob(str(sentence))
                            polarity = sentence_text.sentiment.polarity
                            tweet_time = newData["created_at"]
                            try:
                                datetime_object = time_module.strptime(tweet_time,'%a %b %d %H:%M:%S +0000 %Y')
                                datetime_object = datetime.fromtimestamp(mktime(datetime_object))
                                tweet_time = datetime_object.time()
                            except Exception as e:
                                print(e)
                            #print(str(sentence))
                            #print("polarity " + str(polarity))
                            #print("match time " + str(current_match_time))

                            tweet_sentence = str(sentence)
                            if tweet_about == 1:
                                target = HOME_TEAM
                            else:
                                target = AWAY_TEAM
                            tweet_time = str(tweet_time)
                            try:
                                #print("CURRENT MATCH TIMEEE - " + str(current_match_time))
                                #print(allow_update)
                                if (allow_update == 1) and (polarity != 0):
                                    try:
                                        cursor2.execute("INSERT INTO " + tweetTableName + " (subject, polarity, matchTime, trueTime) VALUES(?,?,?,?)",(target, polarity, current_match_time, tweet_time))
                                        connection2.commit()
                                    except Exception as e:
                                        print(e)
                            except Exception as e:
                                print(e)
        except:
            pass

        return True

    def on_error(self, status):
        print(status)

def updateMatchTime(new_match_time):
    MATCH_TIME = new_match_time

def tableNamePreprocessing(input):
    new_name = input.replace("-", "")
    new_name = new_name.replace(" ", "")
    return new_name

#NEED TO SANITISE TWEET INPUT
def main(homeTeam, awayTeam, tempTableName, date_val):
    print("I HAVE BEEN CALLED")
    global HOME_TEAM
    global AWAY_TEAM
    global tweetTableName
    global cursor2
    global connection2
    global allow_update
    global match_time_table
    tweetTableName = str(tempTableName)+"Tweets"
    tweetTableName = tableNamePreprocessing(tweetTableName)
    match_time_table = homeTeam.lower().replace("-", "_") + awayTeam.lower().replace("-", "_") + date_val + "MatchTime"
    allow_update = 0
    try:
        connection2 = sqlite3.connect("commentary.db")
        cursor2 = connection2.cursor()
    except:
        print("COULD NOT CONNECT TO DATABASE")

    #cursor2.execute("DROP TABLE if exists " + tweetTableName)
    cursor2.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='" + tweetTableName + "';")
    result2 = cursor2.fetchone()
    number_of_rows2 = result2[0]
    print("TABLE NAME OF TWEETS IS - " + tweetTableName)
    if (number_of_rows2 == 0):
        # CREATE TABLE
        create_table_string = "create table if not exists '" + tweetTableName + "' (id INTEGER PRIMARY KEY, subject TEXT, polarity REAL, matchTime TEXT, trueTime TEXT)"
        cursor2.execute(create_table_string)
    allow_update = 1
    # CHANGE THIS ^
    print("MATCH TABLE TIME " + match_time_table)
    HOME_TEAM = str(homeTeam).lower().replace('-', ' ').strip()
    AWAY_TEAM = str(awayTeam).lower().replace('-', ' ').strip()
    print(HOME_TEAM)
    home_team_abbreviation = Team_abbreviations[HOME_TEAM.lower()]
    away_team_abbreviation = Team_abbreviations[AWAY_TEAM.lower()]
    hashtag_list = [home_team_abbreviation+away_team_abbreviation, HOME_TEAM, AWAY_TEAM]
    #hashtag_list = ['Trump']
    print(hashtag_list)
    print("I AM WORKING!!")
    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets(hashtag_list)

#main('chelsea', 'tottenham', '2019', '2020', 'whatever')