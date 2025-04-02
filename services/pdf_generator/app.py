from flask import Flask, request, jsonify, send_file
from fpdf import FPDF
from data_fetcher import fetch_stock_data, fetch_current_price
import numpy as np
import pandas as pd
import os

app = Flask(__name__)
def convert_np_types(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, np.generic):
        return obj.item()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# Custom PDF class to handle styling
class CustomPDF(FPDF):
    def header(self):
        # Add a header with a title
        self.set_font("Arial", style="B", size=14)
        self.set_text_color(50, 50, 50)  # Dark gray
        self.cell(0, 10, "Portfolio Report", align="C", ln=True)
        self.ln(10)

    def footer(self):
        # Add a footer with page numbers
        self.set_y(-15)
        self.set_font("Arial", size=8)
        self.set_text_color(150)  # Light gray
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

# Define a route to generate PDF
@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    try:
        # Get data from the request
        data = request.json
        
        # Fetch additional Yahoo Finance data
        symbol = data.get("symbol", "AAPL")  # Default to Apple
        stock_data = fetch_stock_data(symbol)
        current_price = fetch_current_price(symbol)
        
        # Extract key information from the JSON payload
        role = data.get('role', 'N/A')
        username = data.get('username', 'N/A')
        client_name = data.get('client_name', 'N/A')
        client_email = data.get('client_email', 'N/A')
        portfolio_alias = data.get('portfolio_alias', 'N/A')
        session_frame = data.get('session_frame', {})
        assets_information = data.get('assets_information', {})

        # Create a PDF instance
        pdf = CustomPDF()
        pdf.add_page()

        # Add user and client information section
        pdf.set_font("Arial", style="B", size=12)
        pdf.set_text_color(0)  # Black text
        pdf.cell(0, 10, "Client Information", ln=True)
        
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 8, f"Role: {role}", ln=True)
        pdf.cell(0, 8, f"Username: {username}", ln=True)
        pdf.cell(0, 8, f"Client Name: {client_name}", ln=True)
        pdf.cell(0, 8, f"Client Email: {client_email}", ln=True)
        pdf.cell(0, 8, f"Portfolio Alias: {portfolio_alias}", ln=True)
        
        pdf.ln(10)  # Add spacing

        # Add session_frame table header
        if session_frame:
            pdf.set_font("Arial", style="B", size=12)
            pdf.set_fill_color(200, 220, 255)  # Light blue background for headers
            pdf.cell(30, 10, "Symbol", border=1, fill=True)
            pdf.cell(70, 10, "Name", border=1, fill=True)
            pdf.cell(30, 10, "Last Price", border=1, fill=True)
            pdf.cell(60, 10, "Sector", border=1, fill=True)
            pdf.ln()

            # Add session_frame rows
            symbols = session_frame.get("Symbol", {})
            names = session_frame.get("Name", {})
            prices = session_frame.get("Last Price", {})
            sectors = session_frame.get("Sector", {})

            for i in range(len(symbols)):
                symbol = symbols.get(str(i), "")
                name = names.get(str(i), "")
                price = prices.get(str(i), "")
                sector = sectors.get(str(i), "")

                pdf.set_font("Arial", size=11)
                fill_color = (240 if i % 2 == 0 else 255)  # Alternate row colors (light gray/white)
                pdf.set_fill_color(fill_color)

                pdf.cell(30, 10, symbol[:10], border=1, fill=True)  # Limit symbol length
                pdf.cell(70, 10, name[:30], border=1)               # Limit name length
                pdf.cell(30, 10, f"${price:.2f}", border=1)         # Format price as currency
                pdf.cell(60, 10, sector[:20], border=1)             # Limit sector length
                pdf.ln()

            pdf.ln(10)

        # Add assets_information section
        if assets_information:
            pdf.set_font("Arial", style="B", size=12)
            pdf.cell(0, 10, "Assets Information:", ln=True)

            for symbol, details in assets_information.items():
                name = details.get('name', 'N/A')
                sector = details.get('sector', 'N/A')
                industry = details.get('industry', 'N/A')
                country = details.get('country', 'N/A')

                pdf.set_font("Arial", size=11)
                pdf.multi_cell(
                    0,
                    8,
                    txt=f"Symbol: {symbol}\n"
                        f"Name: {name}\n"
                        f"Sector: {sector}\n"
                        f"Industry: {industry}\n"
                        f"Country: {country}",
                    border="B",
                )
                pdf.ln()

        # Save the PDF to a file
        output_file = "generated_document.pdf"
        pdf.output(output_file)

        # Return the generated PDF as a downloadable file
        return send_file(output_file, as_attachment=True)

    except ValueError as e:
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500
    
# Define a route to fetch stock data
@app.route('/fetch_stock', methods=['GET'])
def fetch_stock():
    try:
        symbol = request.args.get('symbol', 'AAPL')
        stock_data = fetch_stock_data(symbol)
        current_price = fetch_current_price(symbol)

        # Convert Timestamps to strings and numpy types to native types
        stock_data = stock_data.reset_index()
        stock_data['Date'] = stock_data['Date'].dt.strftime('%Y-%m-%d')
        stock_data_json = stock_data.tail(5).to_dict('records')

        return jsonify({
            "symbol": symbol,
            "current_price": float(current_price) if current_price != "N/A" else "N/A",
            "historical_data": stock_data_json
        }), 200, {'Content-Type': 'application/json; charset=utf-8'}
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Health check endpoint (optional)
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "PDF Generator Service is running"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
