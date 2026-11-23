from database.parco_DAO import ParcoDAO
from database.escursione_DAO import EscursioneDAO
from database.punto_interesse_DAO import PuntoInteresseDAO

class Model:
    def __init__(self):
        self.escursioni_map = {} # Mappa ID escursione -> oggetti Escursione
        self.punti_interesse_map = {} # Mappa ID punto di interesse -> oggetti PuntoInteresse

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # TODO: Aggiungere eventuali altri attributi

        # Caricamento
        self.load_escursioni()
        self.load_punti_interesse()
        self.load_relazioni()

    @staticmethod
    def load_parchi():
        """ Restituisce tutti i parchi disponibili """
        return ParcoDAO.get_parchi()

    def load_escursioni(self):
        """ Carica tutte le escursioni in un dizionario [id, Escursione]"""
        self.escursioni_map = EscursioneDAO.get_escursioni()

    def load_punti_interesse(self):
        """ Carica tutti i punti di interesse in un dizionario [id, PuntoInteresse]"""
        self.punti_interesse_map = PuntoInteresseDAO.get_punti_interesse()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra escursioni e punti di interesse e salvarle nelle strutture dati
            Collega escursione <-> punti di interesse.
            --> Ogni Escursione ha un set di PuntoInteresse.
            --> Ogni PuntoInteresse ha un set di Escursioni.
        """
        # TODO
        relazioni = EscursioneDAO.get_escursioni_punti_interesse()
        for row in relazioni:
            escursione = self.escursioni_map.get(row["id_escursione"])
            punto = self.punti_interesse_map.get(row["id_punto_interesse"])
            escursione.punti_interesse.add(punto)
            punto.escursioni.add(escursione)

    def genera_pacchetto(self, id_parco: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto di escursioni ottimale per un parco rispettando i vincoli di durata, budget e punti di interesse unici.
        :param id_parco: id del parco
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Escursione)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il voto complessivo dei visitatori per il pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        # TODO
        self._escursioni_parco = []
        for escur in self.escursioni_map.values():
            if escur.id_parco == id_parco:
                self._escursioni_parco.append(escur)

        self._max_giorni = max_giorni
        self._max_budget = max_budget
        pacchetto_iniziale = []
        punti_iniziali = set()

        self._ricorsione(0,pacchetto_iniziale,0,0.0,0,punti_iniziali)

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, punti_usati: set):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il voto complessivo dei visitatori"""

        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno

        if valore_corrente > self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._pacchetto_ottimo = pacchetto_parziale.copy()
            self._costo = costo_corrente

        for i in range(start_index, len(self._escursioni_parco)):
            escursione = self._escursioni_parco[i]
            nuova_durata = durata_corrente+escursione.durata_giorni
            nuovo_costo = costo_corrente+escursione.costo

            giorni = 0
            budget = 0
            if self._max_giorni is None or nuova_durata <= self._max_giorni:
                giorni = True
            if self._max_budget is None or nuovo_costo <= self._max_budget:
                budget = True

            punti = True
            for punto in escursione.punti_interesse:
                if punto in punti_usati:
                    punti = False

            if giorni and budget and punti:
                valore_escursione = 0
                for punto in escursione.punti_interesse:
                    valore_escursione += punto.voto_visitatori
                    punti_usati.add(punto)
                pacchetto_parziale.append(escursione)
                self._ricorsione(
                    i+1,
                    pacchetto_parziale,
                    nuova_durata,
                    nuovo_costo,
                    valore_corrente+valore_escursione,
                    punti_usati
                )

                pacchetto_parziale.pop()
                for punto in escursione.punti_interesse:
                    punti_usati.remove(punto)


