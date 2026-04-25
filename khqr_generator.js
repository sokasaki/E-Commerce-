const { BakongKHQR, khqrData, IndividualInfo } = require("bakong-khqr");

function generateQR() {
    try {
        const args = process.argv.slice(2);
        if (args.length === 0) {
            console.error("Error: Missing JSON data argument");
            process.exit(1);
        }

        const data = JSON.parse(args[0]);
        
        const {
            bakongAccountId,
            merchantName,
            merchantCity,
            amount,
            currency,
            storeLabel,
            phoneNumber,
            billNumber,
            terminalLabel
        } = data;

        const cur = (currency && currency.toUpperCase() === 'KHR') 
            ? khqrData.currency.khr 
            : khqrData.currency.usd;

        // Correct properties for optionalData
        const optionalData = {
            currency: cur,
            amount: parseFloat(amount) || undefined,
            billNumber: billNumber || undefined,
            mobileNumber: phoneNumber || undefined,
            storeLabel: storeLabel || "MShop",
            terminalLabel: terminalLabel || "Cashier-01",
            expirationTimestamp: Date.now() + (30 * 60 * 1000), // 30 minutes expiry
            merchantCategoryCode: "5999"
        };

        // NEW: In 1.0.20, constructor is (bakongAccountID, merchantName, merchantCity, optionalData)
        const individualInfo = new IndividualInfo(
            bakongAccountId,
            merchantName,
            merchantCity || "Phnom Penh",
            optionalData
        );

        const khqr = new BakongKHQR();
        const response = khqr.generateIndividual(individualInfo);

        if (response && response.data) {
            process.stdout.write(JSON.stringify({
                qr: response.data.qr,
                md5: response.data.md5
            }));
        } else {
            console.error("Error: Unexpected response format: " + JSON.stringify(response));
            process.exit(1);
        }
    } catch (error) {
        console.error("Error: " + error.message);
        process.exit(1);
    }
}

generateQR();
