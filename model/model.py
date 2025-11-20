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

        self._max_giorni = None
        self._max_budget = None

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

    def load_lista_tour_regione(self, regione):
        self.lista_tour_regione = []

        for tour in self.tour_map:
            if tour.id_regione == regione:
                if self._max_giorni is None and self._max_budget is None:
                    self.lista_tour_regione.append(self.tour_map[tour])
                elif self._max_giorni is not None and tour.durata_giorni <= self._max_giorni :
                    self.lista_tour_regione.append(self.tour_map[tour])
                elif self._max_budget is not None and tour.costo <= self._max_budget :
                    self.lista_tour_regione.append(self.tour_map[tour])

    def _is_tour_acceptable(self, tour, durata_corrente, costo_corrente, attrazioni_usate):
        if durata_corrente is None and costo_corrente is None:
            if attrazioni_usate.intersection(tour.attrazioni) is not None:
                return False
        elif durata_corrente is not None and costo_corrente is None:
            if durata_corrente + tour.durata_giorni > self._max_giorni:
                return False
        elif durata_corrente is None and costo_corrente is not None:
            if costo_corrente + tour.costo > self._max_budget:
                return False

        return True

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

        self._max_giorni = max_giorni
        self._max_budget = max_budget

        self.load_lista_tour_regione(id_regione)

        self._ricorsione(0, [], 0, 0, 0, set())

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, attrazioni_usate: set):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""

        # qui dovrei controllare il valore corrente
        # se è minore di quello precedente, allora settare
        # self._pacchetto_ottimo e self._valore_ottimo

        # questa condizione funziona solo se non ci sono vincoli sui giorni e budget
        if self._valore_ottimo == -1 or valore_corrente < self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._pacchetto_ottimo = pacchetto_parziale

        for tour in self.lista_tour_regione[start_index:]:
            # condizioni da controllare (magari con una funzione) :
            # - tour not in pacchetto parziale (controlla che il tour non sia già presente, forse superfluo)
            # - durata_corrente + tour.durata_giorni < self._max_giorni
            # - costo_corrente + tour.costo < self._max_budget
            # - attrazioni_usate.intersection(tour.attrazioni) is None
            #
            # se tutte risultano vere, pacchetto_parziale.append(tour)

            if self._is_tour_acceptable(tour, durata_corrente, costo_corrente, attrazioni_usate):
                pacchetto_parziale.append(tour)
                valore_culturale = sum([attrazione.valore_culturale for attrazione in tour.attrazioni])
                attrazioni_usate.update(tour.attrazioni)
                self._ricorsione(start_index+1,
                                 pacchetto_parziale,
                                 durata_corrente+tour.durata_giorni,
                                 costo_corrente+tour.costo,
                                 valore_corrente+valore_culturale,
                                 attrazioni_usate)

                pacchetto_parziale.pop()
