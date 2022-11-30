{
    address: '',

    setup: function(init) {
        this.address = toAddress(JSON.parse(init).address)
    },


    fault: function(log, db) {},

    result: function(ctx, db) {
        var balance = db.getBalance(this.address)
        return { balance: balance };
    }
}
