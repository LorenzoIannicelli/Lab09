from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        self.lista_tour_regione = []

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """

        relazioni = TourDAO.get_tour_attrazioni()
        for relazione in relazioni :
            self.tour_map[relazione['id_tour']].attrazioni.add(self.attrazioni_map[relazione['id_attrazione']])
            self.attrazioni_map[relazione['id_attrazione']].tour.add(self.tour_map[relazione['id_tour']])

    def load_lista_tour_regione(self, regione, max_giorni, max_budget):
        self.lista_tour_regione = []

        for tour in self.tour_map:
            if tour.id_regione == regione:
                if max_giorni is None and max_budget is None:
                    self.lista_tour_regione.append(tour)
                elif max_giorni is not None and tour.durata_giorni <= max_giorni :
                    self.lista_tour_regione.append(tour)
                elif max_budget is not None and tour.costo <= max_budget :
                    self.lista_tour_regione.append(tour)

    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        self.load_lista_tour_regione(id_regione, max_giorni, max_budget)


        # scorrere i tour controllando il vincolo sulla regione
        # controllare che i giorni complessivi non superi quelli specificati
        # controllare ricorsione dopo ricorsione che costo_corrente non superi quello specificato

        # controllare che il valore ottimo sia maggiore di quello precedente
        # in caso sostituire i valori self._pacchetto_ottimo, self._costo e self._valore_ottimo


        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, attrazioni_usate: set):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""

        for tour in self.lista_tour_regione[start_index:]:
            pass