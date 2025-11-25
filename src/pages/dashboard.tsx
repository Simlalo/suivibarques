import { useState, useMemo, useEffect } from "react";
import { FileUploader } from "@/components/file-uploader";
import Papa from "papaparse";
import {
  Search,
  Calendar,
  Filter,
  Ship,
  Anchor,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  Database,
  Copy
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";

interface Proprietaire {
  [key: string]: string;
}

interface Historique {
  Matricule: string;
  DateMaree: string;
  Mois: number;
  Annee: number;
}

interface MergedData {
  Barque: string;
  Matricule: string;
  DateMaree: string;
  Propriétaire: string;
  Mois: number;
  Annee: number;
  id: string;
}

export default function Dashboard() {
  const { toast } = useToast();
  const [proprietairesData, setProprietairesData] = useState<Proprietaire[]>([]);
  const [historiqueData, setHistoriqueData] = useState<Historique[]>([]);
  const [mergedData, setMergedData] = useState<MergedData[]>([]);
  
  const [selectedProprietaire, setSelectedProprietaire] = useState<string>("all");
  const [barqueFilter, setBarqueFilter] = useState<string>("");
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");

  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const handleProprietairesUpload = (file: File) => {
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        const data = results.data as Proprietaire[];
        console.log("Proprietaires loaded:", data.length);
        setProprietairesData(data);
        toast({
          title: "Fichier Propriétaires chargé",
          description: `${data.length} propriétaires importés avec succès.`,
        });
      },
    });
  };

  const handleHistoriqueUpload = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      const lines = text.split('\n').filter(line => line.trim() !== '');
      
      const data = lines.map(line => {
        const values = line.split(';');
        const dateStr = values[1] ? values[1].trim() : '';
        const dateParts = dateStr.split('/');
        
        return {
          Matricule: values[0] ? values[0].trim() : '',
          DateMaree: dateStr,
          Mois: parseInt(dateParts[0], 10) || 0,
          Annee: parseInt(dateParts[1], 10) || 0
        };
      });
      
      console.log("Historique loaded:", data.length);
      setHistoriqueData(data);
      toast({
        title: "Historique chargé",
        description: `${data.length} entrées d'historique importées.`,
      });
    };
    reader.readAsText(file);
  };

  useEffect(() => {
    if (proprietairesData.length > 0 && historiqueData.length > 0) {
      const merged: MergedData[] = [];
      let idCounter = 0;

      historiqueData.forEach(h => {
        const proprietaire = proprietairesData.find(p => p['Matricule'] === h['Matricule']);
        if (proprietaire) {
          merged.push({
            Barque: proprietaire['Barque'] || 'Inconnu',
            Matricule: h.Matricule,
            DateMaree: h.DateMaree,
            Propriétaire: proprietaire['Propriétaire'] || 'Inconnu',
            Mois: h.Mois,
            Annee: h.Annee,
            id: `row-${idCounter++}`
          });
        }
      });
      
      setMergedData(merged);
      setCurrentPage(1);
    }
  }, [proprietairesData, historiqueData]);

  const filteredData = useMemo(() => {
    let data = mergedData;

    if (selectedProprietaire && selectedProprietaire !== "all") {
      data = data.filter(item => item['Propriétaire'] === selectedProprietaire);
    }

    if (barqueFilter) {
      const lowerFilter = barqueFilter.toLowerCase();
      data = data.filter(item => 
        item['Matricule'].toLowerCase().includes(lowerFilter) || 
        item['Barque'].toLowerCase().includes(lowerFilter)
      );
    }

    if (startDate || endDate) {
      const start = startDate ? new Date(startDate) : null;
      const end = endDate ? new Date(endDate) : null;
      
      if (start) start.setHours(0, 0, 0, 0);
      if (end) end.setHours(23, 59, 59, 999);

      data = data.filter(item => {
        const itemDate = new Date(item.Annee, item.Mois - 1, 1);
        if (start && end) return itemDate >= start && itemDate <= end;
        if (start) return itemDate >= start;
        if (end) return itemDate <= end;
        return true;
      });
    }

    return data;
  }, [mergedData, selectedProprietaire, barqueFilter, startDate, endDate]);

  const uniqueProprietaires = useMemo(() => {
    const props = new Set(mergedData.map(item => item['Propriétaire']));
    return Array.from(props).sort();
  }, [mergedData]);

  const totalPages = Math.ceil(filteredData.length / itemsPerPage);
  const currentData = filteredData.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handleCopyData = () => {
    if (filteredData.length === 0) {
      toast({
        title: "Aucune donnée",
        description: "Il n'y a aucune donnée à copier.",
        variant: "destructive",
      });
      return;
    }

    const itemsText = filteredData.map(item => 
      `⛵ *${item.Barque}* (${item.Matricule})\n📅 ${item.DateMaree}`
    ).join("\n\n------------------\n\n");

    const totalText = `📊 *Total des résultats:* ${filteredData.length}`;
    const textToCopy = `${totalText}\n\n${itemsText}`;

    navigator.clipboard.writeText(textToCopy).then(() => {
      toast({
        title: "Copié dans le presse-papier",
        description: `${filteredData.length} résultats prêts à être collés (WhatsApp/SMS).`,
        duration: 3000,
      });
    }).catch(() => {
      toast({
        title: "Erreur de copie",
        description: "Impossible de copier les données.",
        variant: "destructive",
      });
    });
  };

  return (
    <div className="min-h-screen bg-slate-50/50 p-6 md:p-8 font-sans text-slate-900">
      <div className="max-w-7xl mx-auto space-y-8">
        
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-6">
          <div>
            <h1 className="text-3xl md:text-4xl font-display font-bold text-slate-900 tracking-tight flex items-center gap-3">
              <Anchor className="w-8 h-8 text-primary" />
              Suivi des Marées
            </h1>
            <p className="text-slate-500 mt-2 text-lg">
              Tableau de bord de gestion et recherche par propriétaire
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" className="gap-2" onClick={() => window.location.reload()}>
              <RefreshCw className="w-4 h-4" />
              Réinitialiser
            </Button>
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="bg-white shadow-sm hover:shadow-md transition-shadow border-slate-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Database className="w-5 h-5 text-blue-500" />
                Base Propriétaires
              </CardTitle>
              <CardDescription>Fichier CSV contenant la liste des propriétaires et barques</CardDescription>
            </CardHeader>
            <CardContent>
              <FileUploader 
                id="proprietaires" 
                label="Fichier Propriétaires" 
                accept=".csv" 
                onFileSelect={handleProprietairesUpload} 
              />
              <div className="mt-4 flex justify-between text-sm text-slate-500">
                <span>Statut:</span>
                <span className={proprietairesData.length > 0 ? "text-emerald-600 font-medium" : "text-slate-400"}>
                  {proprietairesData.length > 0 ? `${proprietairesData.length} Entrées` : "En attente"}
                </span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white shadow-sm hover:shadow-md transition-shadow border-slate-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Calendar className="w-5 h-5 text-teal-500" />
                Historique Marées
              </CardTitle>
              <CardDescription>Fichier CSV des dates de marées par matricule</CardDescription>
            </CardHeader>
            <CardContent>
              <FileUploader 
                id="historique" 
                label="Fichier Historique" 
                accept=".csv" 
                onFileSelect={handleHistoriqueUpload} 
              />
              <div className="mt-4 flex justify-between text-sm text-slate-500">
                <span>Statut:</span>
                <span className={historiqueData.length > 0 ? "text-emerald-600 font-medium" : "text-slate-400"}>
                  {historiqueData.length > 0 ? `${historiqueData.length} Entrées` : "En attente"}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-slate-400" />
            <h3 className="text-lg font-semibold text-slate-800">Filtres de Recherche</h3>
          </div>
          
          <Card className="p-6 bg-white shadow-sm border-slate-200">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Propriétaire</label>
                <Select value={selectedProprietaire} onValueChange={setSelectedProprietaire}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Tous les propriétaires" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Tous les propriétaires</SelectItem>
                    {uniqueProprietaires.map((p, idx) => (
                      <SelectItem key={idx} value={p}>{p}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Recherche (Barque/Matricule)</label>
                <div className="relative">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
                  <Input
                    type="text"
                    placeholder="ex: 123-456 ou Nom"
                    className="pl-9"
                    value={barqueFilter}
                    onChange={(e) => setBarqueFilter(e.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Date Début</label>
                <Input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Date Fin</label>
                <Input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                />
              </div>
            </div>
          </Card>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
              Résultats
              <Badge variant="secondary" className="ml-2 bg-blue-100 text-blue-700 hover:bg-blue-100">
                {filteredData.length} trouvés
              </Badge>
            </h3>
            
            {filteredData.length > 0 && (
              <Button variant="outline" onClick={handleCopyData} className="gap-2 text-emerald-600 border-emerald-200 hover:bg-emerald-50 hover:text-emerald-700">
                <Copy className="w-4 h-4" />
                Copier pour WhatsApp
              </Button>
            )}
          </div>

          <div className="rounded-md border border-slate-200 bg-white overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="bg-slate-50 text-slate-500 font-medium border-b border-slate-200">
                  <tr>
                    <th className="px-6 py-4">Barque</th>
                    <th className="px-6 py-4">Matricule</th>
                    <th className="px-6 py-4">Propriétaire</th>
                    <th className="px-6 py-4 text-right">Date Marée</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {currentData.length > 0 ? (
                    currentData.map((item) => (
                      <tr key={item.id} className="hover:bg-slate-50/80 transition-colors">
                        <td className="px-6 py-4 font-medium text-slate-900 flex items-center gap-2">
                          <Ship className="w-4 h-4 text-blue-400" />
                          {item.Barque}
                        </td>
                        <td className="px-6 py-4 text-slate-600 font-mono text-xs">{item.Matricule}</td>
                        <td className="px-6 py-4 text-slate-900">{item.Propriétaire}</td>
                        <td className="px-6 py-4 text-right text-slate-600">{item.DateMaree}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={4} className="px-6 py-12 text-center text-slate-400">
                        {mergedData.length === 0 
                          ? "Veuillez charger les fichiers CSV pour commencer." 
                          : "Aucun résultat ne correspond à vos filtres."}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            
            {filteredData.length > 0 && (
              <div className="bg-slate-50 px-6 py-4 border-t border-slate-200 flex items-center justify-between">
                <span className="text-sm text-slate-500">
                  Page {currentPage} sur {totalPages}
                </span>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}