"""
Modulo per la generazione di report e export
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import xlsxwriter
from io import BytesIO
import tempfile
import os


class ReportGenerator:
    """Gestisce la generazione di report finanziari"""
    
    def __init__(self, db_manager):
        """
        Inizializza il generatore di report
        
        Args:
            db_manager: Istanza di DatabaseManager
        """
        self.db_manager = db_manager
    
    def get_default_period(self) -> tuple:
        """
        Calcola il periodo di default (ultimo mese chiuso)
        
        Returns:
            Tupla (data_inizio, data_fine) nel formato YYYY-MM-DD
        """
        today = datetime.now()
        
        # Primo giorno dell'ultimo mese
        if today.month == 1:
            start_date = datetime(today.year - 1, 12, 1)
        else:
            start_date = datetime(today.year, today.month - 1, 1)
        
        # Ultimo giorno dell'ultimo mese
        if today.month == 1:
            end_date = datetime(today.year - 1, 12, 31)
        else:
            # Trova l'ultimo giorno del mese
            next_month = datetime(today.year, today.month, 1)
            end_date = next_month - timedelta(days=1)
        
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    def generate_dashboard_data(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Genera i dati per la dashboard
        
        Args:
            start_date: Data di inizio periodo (se None, usa periodo default)
            end_date: Data di fine periodo (se None, usa periodo default)
            
        Returns:
            Dizionario con tutti i dati per la dashboard
        """
        if start_date is None or end_date is None:
            start_date, end_date = self.get_default_period()
        
        # Riepilogo finanziario
        financial_summary = self.db_manager.get_financial_summary(start_date, end_date)
        
        # Transazioni del periodo
        transactions = self.db_manager.get_transactions(start_date, end_date)
        
        # Analisi per categoria
        category_analysis = self._analyze_by_category(transactions)
        
        # Trend temporale
        time_trend = self._analyze_time_trend(transactions, start_date, end_date)
        
        return {
            'period': {'start': start_date, 'end': end_date},
            'financial_summary': financial_summary,
            'category_analysis': category_analysis,
            'time_trend': time_trend,
            'transaction_count': len(transactions),
            'charts': self._generate_dashboard_charts(financial_summary, category_analysis, time_trend)
        }
    
    def _analyze_by_category(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analizza le transazioni per categoria"""
        category_data = {}
        
        for transaction in transactions:
            category = transaction['category_name']
            amount = transaction['amount']
            is_income = transaction['is_income']
            is_cogs = transaction['is_cogs']
            
            if category not in category_data:
                category_data[category] = {
                    'name': category,
                    'is_cogs': is_cogs,
                    'income': 0,
                    'expenses': 0,
                    'transaction_count': 0
                }
            
            if is_income:
                category_data[category]['income'] += amount
            else:
                category_data[category]['expenses'] += amount
            
            category_data[category]['transaction_count'] += 1
        
        # Calcola totali
        total_income = sum(cat['income'] for cat in category_data.values())
        total_expenses = sum(cat['expenses'] for cat in category_data.values())
        
        # Aggiungi percentuali
        for category in category_data.values():
            if total_income > 0:
                category['income_percentage'] = (category['income'] / total_income) * 100
            else:
                category['income_percentage'] = 0
            
            if total_expenses > 0:
                category['expense_percentage'] = (category['expenses'] / total_expenses) * 100
            else:
                category['expense_percentage'] = 0
        
        return {
            'categories': list(category_data.values()),
            'total_income': total_income,
            'total_expenses': total_expenses
        }
    
    def _analyze_time_trend(self, transactions: List[Dict[str, Any]], start_date: str, end_date: str) -> Dict[str, Any]:
        """Analizza il trend temporale delle transazioni"""
        if not transactions:
            return {'daily_data': [], 'trend_analysis': {}}
        
        # Converti in DataFrame per facilità di analisi
        df = pd.DataFrame(transactions)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        
        # Raggruppa per data
        daily_summary = df.groupby('transaction_date').agg({
            'amount': lambda x: sum(x[df.loc[x.index, 'is_income'] == True]) - sum(x[df.loc[x.index, 'is_income'] == False]),
            'transaction_id': 'count'
        }).reset_index()
        
        daily_summary.columns = ['date', 'net_amount', 'transaction_count']
        daily_summary['date'] = daily_summary['date'].dt.strftime('%Y-%m-%d')
        
        # Calcola statistiche
        avg_daily_net = daily_summary['net_amount'].mean()
        trend_direction = 'stabile'
        
        if len(daily_summary) > 1:
            first_half = daily_summary[:len(daily_summary)//2]['net_amount'].mean()
            second_half = daily_summary[len(daily_summary)//2:]['net_amount'].mean()
            
            if second_half > first_half * 1.1:
                trend_direction = 'crescente'
            elif second_half < first_half * 0.9:
                trend_direction = 'decrescente'
        
        return {
            'daily_data': daily_summary.to_dict('records'),
            'trend_analysis': {
                'avg_daily_net': float(avg_daily_net),
                'trend_direction': trend_direction,
                'best_day': daily_summary.loc[daily_summary['net_amount'].idxmax()].to_dict() if len(daily_summary) > 0 else None,
                'worst_day': daily_summary.loc[daily_summary['net_amount'].idxmin()].to_dict() if len(daily_summary) > 0 else None
            }
        }
    
    def _generate_dashboard_charts(self, financial_summary: Dict, category_analysis: Dict, time_trend: Dict) -> Dict[str, str]:
        """Genera i grafici per la dashboard"""
        charts = {}
        
        # Grafico a torta delle entrate per categoria
        if category_analysis['categories']:
            income_categories = [cat for cat in category_analysis['categories'] if cat['income'] > 0]
            if income_categories:
                fig_income = go.Figure(data=[go.Pie(
                    labels=[cat['name'] for cat in income_categories],
                    values=[cat['income'] for cat in income_categories],
                    hole=0.3,
                    title="Distribuzione Entrate per Categoria"
                )])
                fig_income.update_layout(title="Entrate per Categoria")
                charts['income_pie'] = fig_income.to_html(include_plotlyjs='cdn', div_id="income_pie")
            
            # Grafico a torta delle uscite per categoria
            expense_categories = [cat for cat in category_analysis['categories'] if cat['expenses'] > 0]
            if expense_categories:
                fig_expenses = go.Figure(data=[go.Pie(
                    labels=[cat['name'] for cat in expense_categories],
                    values=[cat['expenses'] for cat in expense_categories],
                    hole=0.3
                )])
                fig_expenses.update_layout(title="Spese per Categoria")
                charts['expense_pie'] = fig_expenses.to_html(include_plotlyjs='cdn', div_id="expense_pie")
        
        # Grafico del trend temporale
        if time_trend['daily_data']:
            daily_data = time_trend['daily_data']
            
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=[data['date'] for data in daily_data],
                y=[data['net_amount'] for data in daily_data],
                mode='lines+markers',
                name='Profitto Giornaliero',
                line=dict(color='#2E86AB', width=3)
            ))
            
            fig_trend.update_layout(
                title="Trend Profitto Giornaliero",
                xaxis_title="Data",
                yaxis_title="Profitto (€)",
                hovermode='x unified'
            )
            
            charts['trend_line'] = fig_trend.to_html(include_plotlyjs='cdn', div_id="trend_line")
        
        # Grafico a barre riassuntivo
        summary_data = [
            ('Entrate', financial_summary['total_income'], '#27AE60'),
            ('COGS', financial_summary['total_cogs'], '#E74C3C'),
            ('Altre Spese', financial_summary['total_expenses'] - financial_summary['total_cogs'], '#F39C12'),
            ('Profitto Lordo', financial_summary['gross_profit'], '#8E44AD'),
            ('Profitto Netto', financial_summary['net_profit'], '#2C3E50')
        ]
        
        fig_summary = go.Figure(data=[
            go.Bar(
                x=[item[0] for item in summary_data],
                y=[item[1] for item in summary_data],
                marker_color=[item[2] for item in summary_data],
                text=[f"€{item[1]:,.2f}" for item in summary_data],
                textposition='auto'
            )
        ])
        
        fig_summary.update_layout(
            title="Riepilogo Finanziario",
            yaxis_title="Importo (€)",
            showlegend=False
        )
        
        charts['financial_summary'] = fig_summary.to_html(include_plotlyjs='cdn', div_id="financial_summary")
        
        return charts
    
    def export_to_excel(self, start_date: str = None, end_date: str = None, 
                       include_transactions: bool = True) -> str:
        """
        Esporta i dati in un file Excel
        
        Args:
            start_date: Data di inizio periodo
            end_date: Data di fine periodo
            include_transactions: Se includere il dettaglio delle transazioni
            
        Returns:
            Percorso del file Excel creato
        """
        if start_date is None or end_date is None:
            start_date, end_date = self.get_default_period()
        
        # Crea file temporaneo
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"BarFlow_Report_{timestamp}.xlsx"
        file_path = os.path.join(temp_dir, filename)
        
        # Ottieni i dati
        dashboard_data = self.generate_dashboard_data(start_date, end_date)
        transactions = self.db_manager.get_transactions(start_date, end_date) if include_transactions else []
        
        # Crea il file Excel
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Formati
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4CAF50',
                'font_color': 'white',
                'border': 1
            })
            
            currency_format = workbook.add_format({
                'num_format': '€#,##0.00',
                'border': 1
            })
            
            date_format = workbook.add_format({
                'num_format': 'dd/mm/yyyy',
                'border': 1
            })
            
            # Foglio 1: Riepilogo Finanziario
            summary_data = [
                ['Periodo', f"{start_date} - {end_date}"],
                ['', ''],
                ['RIEPILOGO FINANZIARIO', ''],
                ['Entrate Totali', dashboard_data['financial_summary']['total_income']],
                ['COGS (Costi Diretti)', dashboard_data['financial_summary']['total_cogs']],
                ['Altre Spese', dashboard_data['financial_summary']['total_expenses'] - dashboard_data['financial_summary']['total_cogs']],
                ['Spese Totali', dashboard_data['financial_summary']['total_expenses']],
                ['', ''],
                ['Profitto Lordo (Entrate - COGS)', dashboard_data['financial_summary']['gross_profit']],
                ['Profitto Netto (Entrate - Tutte le Spese)', dashboard_data['financial_summary']['net_profit']],
                ['', ''],
                ['ANALISI PERFORMANCE', ''],
                ['Margine Lordo %', (dashboard_data['financial_summary']['gross_profit'] / dashboard_data['financial_summary']['total_income'] * 100) if dashboard_data['financial_summary']['total_income'] > 0 else 0],
                ['Margine Netto %', (dashboard_data['financial_summary']['net_profit'] / dashboard_data['financial_summary']['total_income'] * 100) if dashboard_data['financial_summary']['total_income'] > 0 else 0],
                ['Numero Transazioni', dashboard_data['transaction_count']]
            ]
            
            summary_df = pd.DataFrame(summary_data, columns=['Descrizione', 'Valore'])
            summary_df.to_excel(writer, sheet_name='Riepilogo', index=False, startrow=1, startcol=1)
            
            worksheet = writer.sheets['Riepilogo']
            worksheet.set_column('B:B', 25)
            worksheet.set_column('C:C', 15)
            
            # Applica formati
            for row in range(2, len(summary_data) + 2):
                if row in [5, 6, 7, 8, 10, 11, 14, 15]:  # Righe con valori monetari
                    worksheet.write(row, 2, summary_data[row-2][1], currency_format)
            
            # Foglio 2: Analisi per Categoria
            if dashboard_data['category_analysis']['categories']:
                cat_data = []
                for cat in dashboard_data['category_analysis']['categories']:
                    cat_data.append([
                        cat['name'],
                        'Sì' if cat['is_cogs'] else 'No',
                        cat['income'],
                        cat['expenses'],
                        cat['income'] - cat['expenses'],
                        cat['transaction_count']
                    ])
                
                cat_df = pd.DataFrame(cat_data, columns=[
                    'Categoria', 'COGS', 'Entrate (€)', 'Spese (€)', 'Netto (€)', 'N. Transazioni'
                ])
                cat_df.to_excel(writer, sheet_name='Analisi Categorie', index=False)
                
                cat_worksheet = writer.sheets['Analisi Categorie']
                cat_worksheet.set_column('A:A', 20)
                cat_worksheet.set_column('B:F', 15)
            
            # Foglio 3: Dettaglio Transazioni (se richiesto)
            if include_transactions and transactions:
                trans_data = []
                for trans in transactions:
                    trans_data.append([
                        trans['transaction_date'],
                        trans['description'],
                        trans['category_name'],
                        'Entrata' if trans['is_income'] else 'Uscita',
                        trans['amount'],
                        trans.get('source_filename', 'Manuale')
                    ])
                
                trans_df = pd.DataFrame(trans_data, columns=[
                    'Data', 'Descrizione', 'Categoria', 'Tipo', 'Importo (€)', 'Fonte'
                ])
                trans_df.to_excel(writer, sheet_name='Dettaglio Transazioni', index=False)
                
                trans_worksheet = writer.sheets['Dettaglio Transazioni']
                trans_worksheet.set_column('A:A', 12)
                trans_worksheet.set_column('B:B', 30)
                trans_worksheet.set_column('C:C', 15)
                trans_worksheet.set_column('D:D', 10)
                trans_worksheet.set_column('E:E', 15)
                trans_worksheet.set_column('F:F', 20)
        
        return file_path
    
    def get_monthly_comparison(self, months_back: int = 6) -> Dict[str, Any]:
        """
        Genera un confronto degli ultimi mesi
        
        Args:
            months_back: Numero di mesi da confrontare
            
        Returns:
            Dati di confronto mensile
        """
        monthly_data = []
        
        for i in range(months_back):
            # Calcola il mese
            today = datetime.now()
            target_month = today.month - i
            target_year = today.year
            
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            
            # Primo e ultimo giorno del mese
            start_date = datetime(target_year, target_month, 1)
            if target_month == 12:
                end_date = datetime(target_year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(target_year, target_month + 1, 1) - timedelta(days=1)
            
            # Ottieni dati finanziari
            financial_summary = self.db_manager.get_financial_summary(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            monthly_data.append({
                'month': start_date.strftime('%Y-%m'),
                'month_name': start_date.strftime('%B %Y'),
                **financial_summary
            })
        
        return {
            'monthly_data': list(reversed(monthly_data)),
            'chart': self._generate_monthly_comparison_chart(list(reversed(monthly_data)))
        }
    
    def _generate_monthly_comparison_chart(self, monthly_data: List[Dict]) -> str:
        """Genera grafico di confronto mensile"""
        if not monthly_data:
            return ""
        
        fig = go.Figure()
        
        # Entrate
        fig.add_trace(go.Bar(
            name='Entrate',
            x=[data['month_name'] for data in monthly_data],
            y=[data['total_income'] for data in monthly_data],
            marker_color='#27AE60'
        ))
        
        # Spese
        fig.add_trace(go.Bar(
            name='Spese',
            x=[data['month_name'] for data in monthly_data],
            y=[data['total_expenses'] for data in monthly_data],
            marker_color='#E74C3C'
        ))
        
        # Profitto netto
        fig.add_trace(go.Scatter(
            name='Profitto Netto',
            x=[data['month_name'] for data in monthly_data],
            y=[data['net_profit'] for data in monthly_data],
            mode='lines+markers',
            line=dict(color='#2C3E50', width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Confronto Mensile - Entrate, Spese e Profitto',
            xaxis_title='Mese',
            yaxis_title='Importo (€)',
            yaxis2=dict(
                title='Profitto Netto (€)',
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            legend=dict(x=0, y=1)
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id="monthly_comparison")