from fastmcp.server import FastMCP

# Initialize the FastMCP server
app = FastMCP()

# Define the resource for version pi-43
@app.tool(version='pi-43')
def get_threshold_notification_rules_43() -> str:
    """
    Endpoint to return the rules for usage notification as per TCP compliance for version pi-43.
    """
    return """
    ### 6.5.2 Timing of notifications

    The electronic notifications in clause 6.5.1 must be provided no later than 48 hours after the Customer has reached the following point each month:
    
    a) 50% of the expenditure and/or the Data allowance which forms part of the included value in their plan (and if only one notification is sent by the Supplier, then whichever threshold occurs first);
    
    b) 85% of the expenditure and/or the Data allowance which forms part of the included value in their plan (and if only one notification is sent by the Supplier, then whichever threshold occurs first); and
    
    c) 100% of the expenditure and/or the Data allowance which forms part of the included value in their plan (and if only one notification is sent by the Supplier, then whichever threshold occurs first).
    """

# Define the resource for version pi-44
@app.tool(version='pi-44')
def get_threshold_notification_rules_44() -> str:
    """
    Endpoint to return the rules for usage notification as per TCP compliance for version pi-44.
    """
    return """
    ### 6.5.2 Timing of notifications

    The electronic notifications in clause 6.5.1 must be provided no later than 48 hours after the Customer has reached the following point each month:
    
    a) 50% of the expenditure and/or the Data allowance which forms part of the included value in their plan (and if only one notification is sent by the Supplier, then whichever threshold occurs first);
    
    b) 85% of the expenditure and/or the Data allowance which forms part of the included value in their plan (and if only one notification is sent by the Supplier, then whichever threshold occurs first); and
    
    c) 90% of the expenditure and/or the Data allowance which forms part of the included value in their plan (and if only one notification is sent by the Supplier, then whichever threshold occurs first); and
    
    d) 100% of the expenditure and/or the Data allowance which forms part of the included value in their plan (and if only one notification is sent by the Supplier, then whichever threshold occurs first).
    """

if __name__ == '__main__':
    app.run(transport="streamable-http", port=8082)
