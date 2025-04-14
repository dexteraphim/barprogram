document.addEventListener('DOMContentLoaded', function() {
    const memberSelectElement = document.getElementById('member');

    if (memberSelectElement) {
        const choices = new Choices(memberSelectElement, {
            searchEnabled: true,
            placeholder: false,
            removeItemButton: false,
            itemSelectText: 'Vælg',
            shouldSort: false,
        });

        memberSelectElement.addEventListener('change', function(event) {
            let alpineDataStack = Alpine.closestDataStack(memberSelectElement);
            let alpineComponent = alpineDataStack && alpineDataStack.length > 0 ? alpineDataStack[0] : null;

            if (alpineComponent) {
                let selectedValue = event.target.value;

                if (selectedValue) {
                    fetch(`/member/${selectedValue}/balance`)
                        .then(response => {
                            if (!response.ok) {
                                console.error(`Error fetching balance: ${response.status} ${response.statusText}`);
                                return response.json().then(err => { throw new Error(err.error || 'API error'); });
                            }
                            return response.json();
                         })
                        .then(data => {
                            console.log("Fetched data:", data);

                            if (data.balance !== undefined) {
                                 const newBalanceValue = data.balance;
                                 console.log("Parsed balance (intended):", parseInt(newBalanceValue || 0));

                                 if (typeof alpineComponent.updateCurrentBalance === 'function') {
                                     alpineComponent.updateCurrentBalance(newBalanceValue);
                                 } else {
                                     console.error("updateCurrentBalance method not found on Alpine component data", alpineComponent);
                                 }

                            } else {
                                 console.error("Balance key not found in API response:", data);
                                 if (typeof alpineComponent.updateCurrentBalance === 'function') {
                                     alpineComponent.updateCurrentBalance(0);
                                 }
                            }
                        })
                        .catch(error => {
                            console.error('Error during fetch or processing:', error);
                            if (typeof alpineComponent.updateCurrentBalance === 'function') {
                                alpineComponent.updateCurrentBalance(0);
                            }
                        });

                } else {
                    if (typeof alpineComponent.updateCurrentBalance === 'function') {
                         alpineComponent.updateCurrentBalance(0);
                    }
                    console.log("Selection cleared, balance reset to 0");
                }
            } else {
                console.error("Could not find Alpine component data stack for member select.");
            }
        });

        if (memberSelectElement.value) {
             memberSelectElement.dispatchEvent(new Event('change'));
        }
    }
});