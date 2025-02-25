import re
import math
from bs4 import BeautifulSoup

class SupplyChainReportAnalyzer:
    def __init__(self):
        # Define required KPIs
        self.required_kpis = [
            "Order Fulfillment Cycle Time",
            "On-Time Delivery (OTD)",
            "Inventory Turnover Ratio",
            "Freight Cost per Unit",
            "Perfect Order Rate"
        ]
        
        # Define KPI thresholds
        self.thresholds = {
            "Order Fulfillment Cycle Time": "less than 48 hours",
            "On-Time Delivery (OTD)": "95% or higher",
            "Inventory Turnover Ratio": "above 4",
            "Freight Cost per Unit": "less than $5 per unit",
            "Perfect Order Rate": "≥ 95%"
        }
        
        self.kpi_data = {}
        self.calculated_values = {}
        self.errors = []

    def validate_html(self, html_content):
        """Validate HTML structure and required sections"""
        missing_sections = []
        
        # Check for basic HTML structure
        if "<head>" not in html_content:
            missing_sections.append("<head>")
        if "<body>" not in html_content:
            missing_sections.append("<body>")
        if 'id="kpi-report"' not in html_content and "id='kpi-report'" not in html_content:
            missing_sections.append("<div id='kpi-report'>")
            
        if missing_sections:
            self.errors.append(f"ERROR: Missing required HTML section(s): {', '.join(missing_sections)}.")
            return False
            
        return True

    def parse_html(self, html_content):
        """Parse HTML and extract KPI data"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the KPI report div
        kpi_report = soup.find('div', id='kpi-report')
        if not kpi_report:
            self.errors.append("ERROR: Missing required HTML section(s): kpi-report.")
            return False
            
        # Extract KPI data
        missing_kpis = []
        for kpi in self.required_kpis:
            # Find the KPI heading
            kpi_heading = kpi_report.find(lambda tag: tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] and kpi in tag.text)
            
            if not kpi_heading:
                missing_kpis.append(kpi)
                continue
                
            # Get the next paragraph tags after the heading
            next_tags = kpi_heading.find_next_siblings('p')
            
            # Initialize data for this KPI
            self.kpi_data[kpi] = {}
            
            # Extract values based on the KPI type
            if kpi == "Order Fulfillment Cycle Time":
                # Extract Total Time for All Orders and Number of Orders
                if len(next_tags) >= 2:
                    self.extract_numeric_value(next_tags[0].text, "Total Time for All Orders", kpi)
                    self.extract_numeric_value(next_tags[1].text, "Number of Orders", kpi)
                    
            elif kpi == "On-Time Delivery (OTD)":
                # Extract Orders Delivered On Time and Total Orders Shipped
                if len(next_tags) >= 2:
                    self.extract_numeric_value(next_tags[0].text, "Orders Delivered On Time", kpi)
                    self.extract_numeric_value(next_tags[1].text, "Total Orders Shipped", kpi)
                    
            elif kpi == "Inventory Turnover Ratio":
                # Extract Cost of Goods Sold (COGS) and Average Inventory Value
                if len(next_tags) >= 2:
                    self.extract_numeric_value(next_tags[0].text, "Cost of Goods Sold (COGS)", kpi)
                    self.extract_numeric_value(next_tags[1].text, "Average Inventory Value", kpi)
                    
            elif kpi == "Freight Cost per Unit":
                # Extract Total Freight Cost and Total Units Shipped
                if len(next_tags) >= 2:
                    self.extract_numeric_value(next_tags[0].text, "Total Freight Cost", kpi)
                    self.extract_numeric_value(next_tags[1].text, "Total Units Shipped", kpi)
                    
            elif kpi == "Perfect Order Rate":
                # Extract Orders Delivered Without Issues and Total Orders
                if len(next_tags) >= 2:
                    self.extract_numeric_value(next_tags[0].text, "Orders Delivered Without Issues", kpi)
                    self.extract_numeric_value(next_tags[1].text, "Total Orders", kpi)
        
        if missing_kpis:
            self.errors.append(f"ERROR: Missing required KPI(s): {', '.join(missing_kpis)}.")
            return False
            
        return True

    def extract_numeric_value(self, text, field_name, kpi):
        """Extract numeric value from text and validate"""
        # Extract numeric value using regex
        match = re.search(r':\s*(\d+(?:\.\d+)?)', text)
        if match:
            value = float(match.group(1))
            self.kpi_data[kpi][field_name] = value
        else:
            self.errors.append(f"ERROR: Invalid data type for KPI(s): {field_name}. Please ensure numeric values.")

    def calculate_kpis(self):
        """Calculate all KPIs based on extracted data"""
        # Calculate Order Fulfillment Cycle Time
        if "Order Fulfillment Cycle Time" in self.kpi_data:
            data = self.kpi_data["Order Fulfillment Cycle Time"]
            if "Total Time for All Orders" in data and "Number of Orders" in data:
                total_time = data["Total Time for All Orders"]
                num_orders = data["Number of Orders"]
                if num_orders > 0:
                    cycle_time = total_time / num_orders
                    self.calculated_values["Order Fulfillment Cycle Time"] = round(cycle_time, 2)
        
        # Calculate On-Time Delivery (OTD)
        if "On-Time Delivery (OTD)" in self.kpi_data:
            data = self.kpi_data["On-Time Delivery (OTD)"]
            if "Orders Delivered On Time" in data and "Total Orders Shipped" in data:
                on_time = data["Orders Delivered On Time"]
                total_shipped = data["Total Orders Shipped"]
                if total_shipped > 0:
                    otd_ratio = on_time / total_shipped
                    otd_percentage = otd_ratio * 100
                    self.calculated_values["On-Time Delivery (OTD)"] = round(otd_percentage, 2)
        
        # Calculate Inventory Turnover Ratio
        if "Inventory Turnover Ratio" in self.kpi_data:
            data = self.kpi_data["Inventory Turnover Ratio"]
            if "Cost of Goods Sold (COGS)" in data and "Average Inventory Value" in data:
                cogs = data["Cost of Goods Sold (COGS)"]
                avg_inventory = data["Average Inventory Value"]
                if avg_inventory > 0:
                    turnover_ratio = cogs / avg_inventory
                    self.calculated_values["Inventory Turnover Ratio"] = round(turnover_ratio, 2)
        
        # Calculate Freight Cost per Unit
        if "Freight Cost per Unit" in self.kpi_data:
            data = self.kpi_data["Freight Cost per Unit"]
            if "Total Freight Cost" in data and "Total Units Shipped" in data:
                freight_cost = data["Total Freight Cost"]
                units_shipped = data["Total Units Shipped"]
                if units_shipped > 0:
                    cost_per_unit = freight_cost / units_shipped
                    self.calculated_values["Freight Cost per Unit"] = round(cost_per_unit, 2)
        
        # Calculate Perfect Order Rate
        if "Perfect Order Rate" in self.kpi_data:
            data = self.kpi_data["Perfect Order Rate"]
            if "Orders Delivered Without Issues" in data and "Total Orders" in data:
                perfect_orders = data["Orders Delivered Without Issues"]
                total_orders = data["Total Orders"]
                if total_orders > 0:
                    perfect_ratio = perfect_orders / total_orders
                    perfect_percentage = perfect_ratio * 100
                    self.calculated_values["Perfect Order Rate"] = round(perfect_percentage, 2)

    def generate_executive_summary(self):
        """Generate an executive summary based on calculated KPIs"""
        summary = []
        
        if not self.calculated_values:
            return "Insufficient data to generate an executive summary."
        
        # Analyze Order Fulfillment Cycle Time
        if "Order Fulfillment Cycle Time" in self.calculated_values:
            cycle_time = self.calculated_values["Order Fulfillment Cycle Time"]
            if cycle_time < 48:
                summary.append(f"Order Fulfillment Cycle Time of {cycle_time} hours is within the target threshold of less than 48 hours.")
            else:
                summary.append(f"Order Fulfillment Cycle Time of {cycle_time} hours exceeds the target threshold of less than 48 hours.")
        
        # Analyze On-Time Delivery
        if "On-Time Delivery (OTD)" in self.calculated_values:
            otd = self.calculated_values["On-Time Delivery (OTD)"]
            if otd >= 95:
                summary.append(f"On-Time Delivery rate of {otd}% meets or exceeds the target threshold of 95% or higher.")
            else:
                summary.append(f"On-Time Delivery rate of {otd}% is below the target threshold of 95%, indicating potential reliability issues.")
        
        # Analyze Inventory Turnover Ratio
        if "Inventory Turnover Ratio" in self.calculated_values:
            turnover = self.calculated_values["Inventory Turnover Ratio"]
            if turnover > 4:
                summary.append(f"Inventory Turnover Ratio of {turnover} exceeds the target threshold of above 4, indicating efficient inventory management.")
            else:
                summary.append(f"Inventory Turnover Ratio of {turnover} is below the target threshold of above 4, suggesting potential inventory management issues.")
        
        # Analyze Freight Cost per Unit
        if "Freight Cost per Unit" in self.calculated_values:
            cost_per_unit = self.calculated_values["Freight Cost per Unit"]
            if cost_per_unit < 5:
                summary.append(f"Freight Cost per Unit of ${cost_per_unit} is below the target threshold of less than $5 per unit.")
            else:
                summary.append(f"Freight Cost per Unit of ${cost_per_unit} exceeds the target threshold of less than $5 per unit.")
        
        # Analyze Perfect Order Rate
        if "Perfect Order Rate" in self.calculated_values:
            perfect_rate = self.calculated_values["Perfect Order Rate"]
            if perfect_rate >= 95:
                summary.append(f"Perfect Order Rate of {perfect_rate}% meets or exceeds the target threshold of 95% or higher, reflecting strong operational performance.")
            else:
                summary.append(f"Perfect Order Rate of {perfect_rate}% is below the target threshold of 95%, indicating potential issues in order fulfillment processes.")
        
        # Overall assessment
        strengths = []
        concerns = []
        
        for statement in summary:
            if "exceeds" in statement or "meets" in statement or "within" in statement or "below" in statement and "cost" in statement:
                strengths.append(statement)
            elif "below" in statement or "potential issues" in statement or "potential reliability issues" in statement:
                concerns.append(statement)
        
        overall = []
        if strengths:
            overall.append("Strengths: " + " ".join(strengths))
        if concerns:
            overall.append("Areas for improvement: " + " ".join(concerns))
        
        if len(strengths) > len(concerns):
            overall.insert(0, "Overall, the supply chain is performing well with some areas that could be improved.")
        elif len(strengths) < len(concerns):
            overall.insert(0, "Overall, the supply chain has several performance issues that require attention.")
        else:
            overall.insert(0, "The supply chain shows mixed performance with equal strengths and areas for improvement.")
        
        return "\n".join(overall)

    def generate_report(self):
        """Generate the final structured report"""
        report = []
        
        # Section: Data Validation Report
        validation_report = [
            "# Section: Data Validation Report",
            "- **HTML Structure Verification:** Checked sections include \"<head>\", \"<body>\", and \"<div id='kpi-report'>\"."
        ]
        
        # KPI Presence Verification
        kpi_presence = ["- **KPI Presence Verification:**"]
        for kpi in self.required_kpis:
            status = "Present" if kpi in self.kpi_data else "Missing"
            kpi_presence.append(f"  - {kpi}: [{status}]")
        validation_report.extend(kpi_presence)
        
        # Threshold Check
        threshold_check = ["- **Threshold Check:**"]
        for kpi, threshold in self.thresholds.items():
            threshold_check.append(f"  - {kpi}: {threshold}.")
        validation_report.extend(threshold_check)
        
        # Keyword Identification
        validation_report.append("- **Keyword Identification:**")
        validation_report.append("  Within the \"<div id='kpi-report'>\", identified keywords corresponding to each KPI and extracted the associated numeric values for further calculations.")
        
        report.extend(validation_report)
        report.append("")
        
        # Section: KPI Analysis
        kpi_analysis = ["# Section: KPI Analysis", "For each extracted KPI, the following details are provided:"]
        
        # Order Fulfillment Cycle Time
        ofct_analysis = [
            "1. **Order Fulfillment Cycle Time**",
            f"   - **Extracted Value:** {self.calculated_values.get('Order Fulfillment Cycle Time', 'N/A')}",
            "   - **Calculation Details:**",
            "     - Step 1 – Extract Values: Identify and extract \"Total Time for All Orders\" and \"Number of Orders\".",
            "     - Step 2 – Calculate Cycle Time:",
            "       $\\text{Order Fulfillment Cycle Time} = \\frac{\\text{Total Time for All Orders}}{\\text{Number of Orders}}$",
            "     - Step 3 – Report: Round the result to 2 decimal places."
        ]
        kpi_analysis.extend(ofct_analysis)
        
        # On-Time Delivery (OTD)
        otd_analysis = [
            "2. **On-Time Delivery (OTD)**",
            f"   - **Extracted Value:** {self.calculated_values.get('On-Time Delivery (OTD)', 'N/A')}%",
            "   - **Calculation Details:**",
            "     - Step 1 – Extract Values: Identify and extract \"Orders Delivered On Time\" and \"Total Orders Shipped\".",
            "     - Step 2 – Calculate Ratio:",
            "       $\\text{OTD Ratio} = \\frac{\\text{Orders Delivered On Time}}{\\text{Total Orders Shipped}}$",
            "     - Step 3 – Convert to Percentage:",
            "       $\\text{OTD} = \\text{OTD Ratio} \\times 100$",
            "     - Step 4 – Report: Round the percentage to 2 decimal places."
        ]
        kpi_analysis.extend(otd_analysis)
        
        # Inventory Turnover Ratio
        itr_analysis = [
            "3. **Inventory Turnover Ratio**",
            f"   - **Extracted Value:** {self.calculated_values.get('Inventory Turnover Ratio', 'N/A')}",
            "   - **Calculation Details:**",
            "     - Step 1 – Extract Values: Identify and extract \"Cost of Goods Sold (COGS)\" and \"Average Inventory Value\".",
            "     - Step 2 – Calculate Ratio:",
            "       $\\text{Inventory Turnover Ratio} = \\frac{\\text{COGS}}{\\text{Average Inventory Value}}$",
            "     - Step 3 – Report: Round the result to 2 decimal places."
        ]
        kpi_analysis.extend(itr_analysis)
        
        # Freight Cost per Unit
        fcpu_analysis = [
            "4. **Freight Cost per Unit**",
            f"   - **Extracted Value:** ${self.calculated_values.get('Freight Cost per Unit', 'N/A')}",
            "   - **Calculation Details:**",
            "     - Step 1 – Extract Values: Identify and extract \"Total Freight Cost\" and \"Total Units Shipped\".",
            "     - Step 2 – Calculate Cost:",
            "       $\\text{Freight Cost per Unit} = \\frac{\\text{Total Freight Cost}}{\\text{Total Units Shipped}}$",
            "     - Step 3 – Report: Round the result to 2 decimal places."
        ]
        kpi_analysis.extend(fcpu_analysis)
        
        # Perfect Order Rate
        por_analysis = [
            "5. **Perfect Order Rate**",
            f"   - **Extracted Value:** {self.calculated_values.get('Perfect Order Rate', 'N/A')}%",
            "   - **Calculation Details:**",
            "     - Step 1 – Extract Values: Identify and extract \"Orders Delivered Without Issues\" and \"Total Orders\".",
            "     - Step 2 – Calculate Ratio:",
            "       $\\text{Perfect Order Ratio} = \\frac{\\text{Orders Delivered Without Issues}}{\\text{Total Orders}}$",
            "     - Step 3 – Convert to Percentage:",
            "       $\\text{Perfect Order Rate} = \\text{Perfect Order Ratio} \\times 100$",
            "     - Step 4 – Report: Round the percentage to 2 decimal places."
        ]
        kpi_analysis.extend(por_analysis)
        
        kpi_analysis.append("- *Note:* If no historical data is provided for any KPI, simply report the extracted KPI value without further calculations.")
        
        report.extend(kpi_analysis)
        report.append("")
        
        # Section: Executive Summary
        executive_summary = [
            "# Section: Executive Summary",
            self.generate_executive_summary()
        ]
        report.extend(executive_summary)
        report.append("")
        
        # Section: Feedback Request
        feedback_request = [
            "# Section: Feedback Request",
            "\"Would you like detailed calculations for any specific KPI? Rate this analysis (1-5).\""
        ]
        report.extend(feedback_request)
        
        return "\n".join(report)

    def analyze_report(self, html_content):
        """Main function to analyze the HTML report and generate the final report"""
        if not self.validate_html(html_content):
            return "\n".join(self.errors)
            
        if not self.parse_html(html_content):
            return "\n".join(self.errors)
            
        self.calculate_kpis()
        
        return self.generate_report()

def process_html_report(html_content):
    """Process the HTML report and return the analysis"""
    analyzer = SupplyChainReportAnalyzer()
    return analyzer.analyze_report(html_content)

def handle_greeting(message):
    """Handle greeting based on message content"""
    response = ""
    
    # Check for urgency words
    if any(word in message.lower() for word in ["urgent", "asap", "emergency"]):
        response = "SupplyChainReport-AI here! Let's quickly review your supply chain report."
    # Check for name
    elif "my name is" in message.lower() or "i am" in message.lower():
        # Extract name (simplified approach)
        match = re.search(r"(my name is|i am)\s+(\w+)", message.lower())
        if match:
            name = match.group(2).capitalize()
            response = f"Hello, {name}! I am SupplyChainReport-AI, here to help analyze your supply chain report."
    # Check for time of day
    elif "morning" in message.lower():
        response = "Good morning! SupplyChainReport-AI is ready to assist you."
    elif "afternoon" in message.lower():
        response = "Good afternoon! Let's review your supply chain report together."
    elif "evening" in message.lower():
        response = "Good evening! I'm here to help analyze your report."
    elif "night" in message.lower():
        response = "Hello! SupplyChainReport-AI is working late to assist you."
    else:
        response = "Greetings! I am SupplyChainReport-AI, your supply chain analysis assistant. Please share your HTML report in a markdown code block labeled as HTML to begin."
    
    return response

def handle_feedback(rating):
    """Handle feedback based on rating"""
    rating = int(rating)
    
    if rating == 1:
        return "We appreciate your honest feedback. Please let us know what specific improvements you would like."
    elif rating == 2:
        return "Thank you for your input. Could you share how we might make the analysis clearer or more comprehensive?"
    elif rating == 3:
        return "Thank you for your rating. Please advise on what additional details or explanations would be helpful."
    elif rating == 4:
        return "Thank you for your positive feedback! We're glad the analysis was helpful."
    elif rating == 5:
        return "Thank you for your excellent feedback! We're delighted that our analysis exceeded your expectations."
    else:
        return "Thank you for your feedback. Please rate the analysis on a scale of 1-5."

def provide_template():
    """Provide a template for the HTML report"""
    template = """Here is the sample template for HTML input:

HTML Report Template Example:

```HTML
<!DOCTYPE html>
<html>
  <head>
    <title>Supply Chain KPI Report</title>
  </head>
  <body>
    <div id="kpi-report">
      <h2>Order Fulfillment Cycle Time</h2>
      <p>Total Time for All Orders: [value]</p>
      <p>Number of Orders: [value]</p>

      <h2>On-Time Delivery (OTD)</h2>
      <p>Orders Delivered On Time: [value]</p>
      <p>Total Orders Shipped: [value]</p>

      <h2>Inventory Turnover Ratio</h2>
      <p>Cost of Goods Sold (COGS): [value]</p>
      <p>Average Inventory Value: [value]</p>

      <h2>Freight Cost per Unit</h2>
      <p>Total Freight Cost: [value]</p>
      <p>Total Units Shipped: [value]</p>

      <h2>Perfect Order Rate</h2>
      <p>Orders Delivered Without Issues: [value]</p>
      <p>Total Orders: [value]</p>
    </div>
  </body>
</html>
```
Please provide your data in HTML format only."""
    return template

def main():
    """Main function to process user input and generate response"""
    message = input("Enter your message: ")
    
    # Check if message is in English
    # This is a simple check and can be improved with language detection libraries
    if not all(ord(c) < 128 for c in message.replace(" ", "")):
        return "ERROR: Unsupported language detected. Please use ENGLISH."
    
    # Check if message is asking for a template
    if "template" in message.lower():
        return provide_template()
    
    # Check if message contains a markdown code block labeled as HTML
    html_match = re.search(r"```HTML\s+(.*?)\s+```", message, re.DOTALL)
    if html_match:
        html_content = html_match.group(1)
        return process_html_report(html_content)
    
    # Check if message contains a rating
    rating_match = re.search(r"rate\s+(\d+)", message.lower())
    if rating_match:
        return handle_feedback(rating_match.group(1))
    
    # Default to greeting
    return handle_greeting(message)


# Add this at the bottom of your script, replacing your current main block
if __name__ == "__main__":
    # Define the HTML content directly
    html_content = """<!DOCTYPE html>
    <html>
    <head>
        <title>Supply Chain KPI Report</title>
    </head>
    <body>
        <div id="kpi-report">
        <h2>Order Fulfillment Cycle Time</h2>
        <p>Total Time for All Orders: 600</p>
        <p>Number of Orders: 25</p>
        
        <h2>On-Time Delivery (OTD)</h2>
        <p>Orders Delivered On Time: 22</p>
        <p>Total Orders Shipped: 25</p>
        
        <h2>Inventory Turnover Ratio</h2>
        <p>Cost of Goods Sold (COGS): 15000</p>
        <p>Average Inventory Value: 3000</p>
        
        <h2>Freight Cost per Unit</h2>
        <p>Total Freight Cost: 90</p>
        <p>Total Units Shipped: 40</p>
        
        <h2>Perfect Order Rate</h2>
        <p>Orders Delivered Without Issues: 20</p>
        <p>Total Orders: 25</p>
        </div>
    </body>
    </html>

"""
    
    # Process the HTML content and print the report
    report = process_html_report(html_content)
    print(report)