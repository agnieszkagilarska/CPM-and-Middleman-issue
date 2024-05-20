import numpy as np

class MiddleMan:
    """
    # Example usage
    >>> mm = MiddleMan()
    >>> mm.add_supplier('D1', 20, 10)
    >>> mm.add_supplier('D2', 30, 12)

    >>> mm.add_receiver('O1', 10, 30)
    >>> mm.add_receiver('O2', 28, 25)
    >>> mm.add_receiver('O3', 27, 30)

    >>> transport_cost_matrix = np.array([
    >>>     [8, 14, 17],
    >>>     [12, 9, 19]
    >>> ])

    >>> mm.add_transport_matrix(transport_cost_matrix)

    >>> mm.calculate()
    'Optimal'
    >>> mm.calculate_overall_return()
    260.0
    >>> mm.calculate_returns()
    array([[120.,   0.,  30.],
           [  0., 112.,  -2.]])
    """
    def __init__(self, supp_idx=1, rec_idx=1):
        self.supp_idx = supp_idx
        self.rec_idx = rec_idx
        self.suppliers = []
        self.receivers = []
    
    def calculate(self):
        self.unit_profits = self.unit_profits_matrix()
        self.indices = self.calc_sorted_indices()
        
        supp_sum, dmnd_sum = self.supply_demand_sum()
        
        if supp_sum != dmnd_sum:
            self.unit_profits = np.pad(self.unit_profits, ((0, 1), (0, 1)), 'constant', constant_values=0)
            self.transport_cost_matrix = np.pad(self.transport_cost_matrix, ((0, 1), (0, 1)), 'constant', constant_values=0)
            self.suppliers.append(('DF', dmnd_sum, 0))
            self.receivers.append(('OF', supp_sum, 0))
        
        self.sales, supp, recv = self.sales_matrix()
        alphas, betas = self._calculate_alpha_beta()
        deltas = self.calculate_deltas(alphas, betas)
        
        if np.any(deltas > 0):
            return "Suboptimal"
        else:
            return "Optimal"
        
    def add_supplier(self, name, supply, cost):
        self.suppliers.append((name, supply, cost))
        
    def add_receiver(self, name, demand, price):
        self.receivers.append((name, demand, price))
        
    def add_transport_matrix(self, matrix:np.ndarray):
        self.transport_cost_matrix = matrix
        
    def unit_profits_matrix(self):
        un_pr_matrix = np.empty_like(self.transport_cost_matrix)
        # Suppliers
        for i, row in enumerate(self.transport_cost_matrix):
            # Receivers
            for j, num in enumerate(row):
                
                un_pr_matrix[i, j] = self.receivers[j][2] - self.suppliers[i][2] - self.transport_cost_matrix[i, j]
        
        return un_pr_matrix

    def supply_demand_sum(self):
        supp_sum = sum([supp[self.supp_idx] for supp in self.suppliers])
        dmnd_sum = sum([recv[self.rec_idx] for recv in self.receivers])
        return supp_sum, dmnd_sum
    
    def calc_sorted_indices(self):
        indices = np.argsort(self.unit_profits, axis=None)[::-1]
        indices = np.unravel_index(indices, self.unit_profits.shape)
        return indices
    
    def sales_matrix(self):
        suppliers_cpy = [list(tup) for tup in self.suppliers]
        receivers_cpy = [list(tup) for tup in self.receivers]
        # We start from REAL Suppliers and Receivers:
        sales = np.zeros(self.unit_profits.shape)
        for idx, jdx in zip(*self.indices):
            # Each iteration is one supplier-receiver transaction
            unit_profit = self.unit_profits[idx, jdx]
            supp_name, supply, cost = suppliers_cpy[idx]
            recv_name, demand, price = receivers_cpy[jdx]
            if supply == 0 or demand == 0:
                continue
            
            supply_after = supply - demand
            if supply_after >= 0:
                # no supply
                sales[idx, jdx] = demand
                
                # Update
                suppliers_cpy[idx][self.supp_idx] = supply_after
                receivers_cpy[jdx][self.rec_idx]  = 0
            if supply_after < 0:
                # no demand
                sales[idx, jdx] = supply
                
                # Update
                suppliers_cpy[idx][self.supp_idx] = 0
                receivers_cpy[jdx][self.rec_idx]  = -supply_after
        
        # We go to FICTIONAL Suppliers and Receivers
        for idx, row in enumerate(sales):
            for jdx, num in enumerate(row):
                # Each iteration is one supplier-receiver transaction
                unit_profit = self.unit_profits[idx, jdx]
                supp_name, supply, cost = suppliers_cpy[idx]
                recv_name, demand, price = receivers_cpy[jdx]
                if supply == 0 or demand == 0:
                    continue
                
                supply_after = supply - demand
                if supply_after >= 0:
                    # no supply
                    sales[idx, jdx] = demand
                    
                    # Update
                    suppliers_cpy[idx][self.supp_idx] = supply_after
                    receivers_cpy[jdx][self.rec_idx]  = 0
                if supply_after < 0:
                    # no demand
                    sales[idx, jdx] = supply
                    
                    # Update
                    suppliers_cpy[idx][self.supp_idx] = 0
                    receivers_cpy[jdx][self.rec_idx]  = -supply_after
                
        if (sum([supp[self.supp_idx] for supp in suppliers_cpy]) or
            sum([recv[self.rec_idx] for recv in receivers_cpy])):
            raise Exception("Supply and Demand after calculations are not zero.")
        return sales, suppliers_cpy, receivers_cpy
    
    def _calculate_alpha_beta(self):
        mask = self.sales[:-1, :-1] !=0
        masked_array = (self.unit_profits[:-1, :-1] * mask)

        A = []
        B = []
        for i in range(mask.shape[0]):
            for j in range(mask.shape[1]):
                if mask[i, j]:
                    row = [0]*(mask.shape[0] + mask.shape[1])
                    row[i] = 1
                    row[mask.shape[0] + j] = 1
                    A.append(row)
                    B.append(masked_array[i, j])

        A = np.array(A)
        B = np.array(B)
        
        solution, residuals, rank, s = np.linalg.lstsq(A, B, rcond=None)

        alphas = np.append(solution[:2], 0)
        betas = np.append(solution[2:], 0)
        
        return alphas, betas
    
    def calculate_deltas(self, alphas, betas):
        # Step 5 in algorithm
        deltas = np.zeros(self.unit_profits.shape)
        for idx, row in enumerate(self.unit_profits[:-1][:-1]):
            for jdx, unit_profit in enumerate(row):
                deltas[idx, jdx] = round(unit_profit - alphas[idx] - betas[jdx], 4)
        
        return deltas
    
    def calculate_overall_return(self):
        return np.sum(self.unit_profits[:-1, :-1] * self.sales[:-1, :-1])

    def calculate_returns(self):
        return self.unit_profits[:-1, :-1] * self.sales[:-1, :-1]