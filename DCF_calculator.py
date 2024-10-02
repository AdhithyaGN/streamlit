

class dcf_calculation:

    def __init__(self) -> None:
        pass


    def intrinsic_pe(self,coc,roce,growth_rate,high_growth_period,fade_period,terminal_growth_rate
                     ):
        """ 
        This function calculates the intrinsic pe value for the given stock using the parameters 
        coc:Cost of Capital,
        roce:Return on Capital employed,
        Growth rate,
        high_growth_period,
        terminal_growth_rate etc.
        """

        try:

        


            self.coc=coc
            self.roce=roce
            self.gr=growth_rate
            self.hgp=high_growth_period
            self.fp=fade_period
            self.tgr=terminal_growth_rate


            RoC=self.roce/100
            Tax_Rate=0.25
            RoC_posttax=RoC*(1-Tax_Rate)
            CoC=self.coc/100

            Earnings_growth_15_years=self.gr/100
            growth_period=self.hgp
            fade_period=self.fp
            Terminal_growth_rate=self.tgr/100
            Reinvestment_rate1=Earnings_growth_15_years/RoC_posttax

            Reinvestment_rate2=Terminal_growth_rate/RoC_posttax
            Year=[x for x in range(-1,growth_period+fade_period+1)]
            initialiser1=0
            initialiser2=100
            Earnings_growth_rate={}
            EBT={}
            NOPAT={}
            Capital_ending={}
            Investment={}
            FCF={}
            Discount_factor={}
            Discounted_FCF={}
            for i in Year:
                Earnings_growth_rate[i]=initialiser1
                EBT[i]=initialiser1
                NOPAT[i]=initialiser1
                Capital_ending[i]=initialiser2
                Investment[i]=initialiser1
                FCF[i]=initialiser1
                Discount_factor[i]=initialiser1
                Discounted_FCF[i]=initialiser1

            NOPAT[0]=Capital_ending[-1]*RoC_posttax

            Investment[0]=NOPAT[0]*Reinvestment_rate1

            Capital_ending[0]=Capital_ending[-1]+Investment[0]

            EBT[0]=NOPAT[0]/(1-Tax_Rate)


            FCF[0]=NOPAT[0]-Investment[0]


            for i in range(1,growth_period+1):
                NOPAT[i]=Capital_ending[i-1]*RoC_posttax
                Investment[i]=NOPAT[i]*Reinvestment_rate1
                Capital_ending[i]=Capital_ending[i-1]+Investment[i]
                FCF[i]=NOPAT[i]-Investment[i]
                Earnings_growth_rate[i]=NOPAT[i]/NOPAT[i-1]-1

            for i in range(growth_period+1,growth_period+fade_period+1):
                Earnings_growth_rate[i]=Earnings_growth_rate[i-1]-(Earnings_growth_15_years-Terminal_growth_rate)/fade_period
                NOPAT[i]=Capital_ending[i-1]*RoC_posttax
                Investment[i]=Earnings_growth_rate[i]/RoC_posttax*NOPAT[i]
                Capital_ending[i]=Capital_ending[i-1]+Investment[i]
                FCF[i]=NOPAT[i]-Investment[i]


            Discount_factor={}
            Discounted_FCF={}

            for i in range(growth_period+fade_period+1):
                EBT[i]=NOPAT[i]/(1-Tax_Rate)
                Discount_factor[i]=1/(1+CoC)**i
                Discounted_FCF[i]=Discount_factor[i]*FCF[i]
            Terminal_NOPAT=NOPAT[growth_period+fade_period]*(1+Terminal_growth_rate)/(CoC-Terminal_growth_rate)

            Terminal_Investment=Terminal_NOPAT*Reinvestment_rate2


            Terminal_FCF=Terminal_NOPAT-Terminal_Investment

            Terminal_DiscountFactor=Discount_factor[growth_period+fade_period]

            Terminal_Discounted_FCF=Terminal_FCF*Terminal_DiscountFactor

            Intrinsic_value=sum(Discounted_FCF.values(),Terminal_Discounted_FCF)

            Intrinsic_PE=Intrinsic_value/NOPAT[0]


            self.intrinsic_pe_value=round(Intrinsic_PE,2)

            return self.intrinsic_pe_value

        except Exception as e:
            raise e
        

    def degree_of_overvaluation(self,intrinsic_pe,current_pe,fy23_pe):

        """
        The degree of overvaluation is calculated as follows:
        if current PE < FY23PE, degree of overvaluation = (current PE/calculated intrinsic PE)  1, 
        else degree of overvaluation = (FY23 PE/calculated intrinsic PE) - 1


        """

        try:

            if float(current_pe)<fy23_pe:
                self.degree_of_overval=round(((float(current_pe)/intrinsic_pe)-1)*100)

            else:
                self.degree_of_overval=round(((fy23_pe/intrinsic_pe)-1)*100)


            return self.degree_of_overval
        


        except Exception as e:
            raise e
        


